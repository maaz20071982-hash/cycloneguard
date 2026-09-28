"""
CycloneGuard Rapid Intensification Dataset Builder.

Constructs reproducible, leakage-free datasets from multi-source observations and track series.
Enforces:
1. Directional temporal causality (feature_time < target_time)
2. Strict isolation of future target variables from state representations
3. Explicit missingness tracking (value + availability indicator)
4. Storm-wise partition filtering without random shuffling
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import os
from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np

from ml.data.schemas.track import CycloneTrackPoint, CycloneTrackSeries
from ml.data.schemas.satellite import CycloneCenteredCrop
from ml.features.cyclone_state import CycloneState, CycloneStateBuilder
from ml.features.state_encoder import CycloneStateEncoder
from ml.data.sequences.ri_label import RILabelGenerator, RILabelResult


@dataclass
class RIDatasetItem:
    """
    A single supervised/unsupervised training observation for RI prediction.
    """
    storm_id: str
    storm_name: Optional[str]
    observation_time_utc: str
    latitude: float
    longitude: float
    forecast_horizon_hours: float
    
    # Feature representation
    cyclone_state: CycloneState
    feature_vector: np.ndarray  # Shape: (69,)
    
    # Sub-feature groups for inspectability
    current_state_features: Dict[str, Any]
    temporal_features: Dict[str, Any]
    source_availability_indicators: Dict[str, bool]
    cross_source_features: Dict[str, Any]
    data_quality_features: Dict[str, Any]
    
    # Target variables (strictly future; excluded from feature vector)
    target_time_utc: Optional[str] = None
    target_intensity_kts: Optional[float] = None
    delta_intensity_kts: Optional[float] = None
    ri_target: Optional[int] = None  # 1 = RI, 0 = Non-RI, None = Unavailable
    is_target_available: bool = False
    target_status: str = "UNAVAILABLE"


class RIDataset:
    """
    Collection of RIDatasetItem records with storm-wise filtering and matrix export.
    """

    def __init__(self, items: List[RIDatasetItem]):
        self.items = items

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, idx: int) -> RIDatasetItem:
        return self.items[idx]

    def get_supervised_items(self) -> List[RIDatasetItem]:
        """Return only records where a valid, verified future target exists."""
        return [item for item in self.items if item.is_target_available and item.ri_target is not None]

    def filter_by_storm_ids(self, storm_ids: Set[str]) -> "RIDataset":
        """Filter dataset to include only items from designated storm IDs."""
        filtered = [item for item in self.items if item.storm_id in storm_ids]
        return RIDataset(filtered)

    def to_numpy(
        self,
        supervised_only: bool = True,
        feature_indices: Optional[List[int]] = None,
    ) -> Tuple[np.ndarray, np.ndarray, List[Dict[str, Any]]]:
        """
        Export dataset to NumPy matrices for ML training or evaluation.
        
        Args:
            supervised_only: If True, exports only items with valid ri_target.
            feature_indices: Optional subset of column indices to extract.
            
        Returns:
            X: 2D array of features (N, D)
            y: 1D array of binary RI labels (N,)
            metadata: List of provenance dicts for each row
        """
        target_items = self.get_supervised_items() if supervised_only else self.items
        if not target_items:
            return np.empty((0, 69)), np.empty((0,), dtype=int), []

        X_full = np.vstack([item.feature_vector for item in target_items])
        if feature_indices is not None:
            X = X_full[:, feature_indices]
        else:
            X = X_full

        y = np.array([item.ri_target if item.ri_target is not None else -1 for item in target_items], dtype=int)
        
        metadata = [
            {
                "storm_id": item.storm_id,
                "storm_name": item.storm_name,
                "observation_time_utc": item.observation_time_utc,
                "target_time_utc": item.target_time_utc,
                "current_wind_kts": item.cyclone_state.intensity.value,
                "delta_wind_kts": item.delta_intensity_kts,
                "ri_target": item.ri_target,
            }
            for item in target_items
        ]

        return X, y, metadata


class RIDatasetBuilder:
    """
    Constructs a complete RIDataset from raw track series and satellite caches.
    """

    def __init__(
        self,
        encoder: Optional[CycloneStateEncoder] = None,
        forecast_horizon_hours: float = 24.0,
        ri_threshold_kts: float = 30.0,
        time_tolerance_hours: float = 2.5,
    ):
        self.encoder = encoder or CycloneStateEncoder()
        self.forecast_horizon_hours = forecast_horizon_hours
        self.ri_threshold_kts = ri_threshold_kts
        self.time_tolerance_hours = time_tolerance_hours

    def build_from_storms(
        self,
        storms: Dict[str, CycloneTrackSeries],
        crops_by_storm_and_time: Optional[Dict[str, Dict[str, CycloneCenteredCrop]]] = None,
    ) -> RIDataset:
        """
        Transform all storm tracks into an RIDataset.
        """
        items: List[RIDatasetItem] = []
        crops = crops_by_storm_and_time or {}

        for storm_id, series in storms.items():
            pts = series.points
            storm_crops = crops.get(storm_id, {})

            for i, current_pt in enumerate(pts):
                # Retrospective points strictly <= current time
                prev_pt = pts[i - 1] if i > 0 else None
                h6_pt = pts[i - 2] if i > 1 else None
                h12_pt = pts[i - 4] if i > 3 else None

                # Find coincident crop if available
                sat_crop = storm_crops.get(current_pt.timestamp_utc)

                # 1. Build CycloneState
                state = CycloneStateBuilder.build_state(
                    current_track=current_pt,
                    previous_track=prev_pt,
                    hist_6h_track=h6_pt,
                    hist_12h_track=h12_pt,
                    satellite_crop=sat_crop,
                )

                # 2. Encode state vector
                feature_vec = self.encoder.encode(state)

                # 3. Derive strictly future target label
                label_res = RILabelGenerator.generate_label(
                    current_point=current_pt,
                    track_series=series,
                    horizon_hours=self.forecast_horizon_hours,
                    threshold_kts=self.ri_threshold_kts,
                    tolerance_hours=self.time_tolerance_hours,
                )

                # 4. Mandatory Leakage Firewall Checks
                t0_dt = datetime.fromisoformat(str(current_pt.timestamp_utc).replace("Z", "+00:00"))
                target_dt_str = label_res.target_time_utc
                if target_dt_str:
                    target_dt = datetime.fromisoformat(target_dt_str.replace("Z", "+00:00"))
                    assert target_dt > t0_dt, f"Leakage violation: Target time {target_dt} <= Feature time {t0_dt}"

                # Verify target intensity was not leaked into current state intensity
                assert state.intensity.value == current_pt.wind_speed_kts, "Current state intensity corrupted!"

                item = RIDatasetItem(
                    storm_id=storm_id,
                    storm_name=series.storm_name,
                    observation_time_utc=current_pt.timestamp_utc,
                    latitude=current_pt.latitude,
                    longitude=current_pt.longitude,
                    forecast_horizon_hours=self.forecast_horizon_hours,
                    cyclone_state=state,
                    feature_vector=feature_vec,
                    current_state_features=state.track_features,
                    temporal_features=state.temporal_features,
                    source_availability_indicators=state.data_quality,
                    cross_source_features=state.cross_source_features,
                    data_quality_features=state.data_quality,
                    target_time_utc=label_res.target_time_utc,
                    target_intensity_kts=label_res.future_wind_kts,
                    delta_intensity_kts=label_res.delta_wind_kts,
                    ri_target=1 if label_res.is_ri is True else (0 if label_res.is_ri is False else None),
                    is_target_available=(label_res.status == "AVAILABLE"),
                    target_status=label_res.status,
                )
                items.append(item)

        return RIDataset(items)


def verify_dataset_partitions_disjoint(
    train_dataset: RIDataset,
    val_dataset: RIDataset,
    test_dataset: RIDataset,
) -> None:
    """
    Asserts zero storm identity leakage across dataset partitions.
    """
    train_storms = {item.storm_id for item in train_dataset.items}
    val_storms = {item.storm_id for item in val_dataset.items}
    test_storms = {item.storm_id for item in test_dataset.items}

    assert train_storms.isdisjoint(val_storms), f"Leakage detected: Train & Val share {train_storms & val_storms}"
    assert train_storms.isdisjoint(test_storms), f"Leakage detected: Train & Test share {train_storms & test_storms}"
    assert val_storms.isdisjoint(test_storms), f"Leakage detected: Val & Test share {val_storms & test_storms}"
