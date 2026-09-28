"""
CycloneGuard Spatial Rapid Intensification Dataset Builder.
Sprint 9 - Phase 4 Deliverable.

Constructs an interpretable spatial dataset for 24-hour Rapid Intensification (RI)
prediction, pairing physical HURSAT-B1 satellite patches with verified ground-truth targets.

Guarantees:
1. Strict preservation of Sprint 8 verified RI ground-truth labels and horizon.
2. Complete storm-wise partition isolation (Train: Phailin, Helen, Hudhud, Nilofar; Val: Megh; Test: Chapala).
3. Explicit missingness tracking (availability indicators; NEVER zero-filling unobserved channels).
4. Directional causality: features derived only from contemporaneous observations (t <= t_0).
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
import json
import os
from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np
import pandas as pd

from ml.data.schemas.track import CycloneTrackPoint
from ml.features.satellite_spatial import SatelliteSpatialFeatureExtractor, SpatialFeatureConfig
from ml.features.track_features import TrackFeatureExtractor
from ml.features.temporal_features import TemporalFeatureExtractor


# Canonical list of 38 spatial features from the registry
SPATIAL_FEATURE_NAMES: Tuple[str, ...] = (
    # Family A: Bulk IR Statistics (12)
    "irwin_mean",
    "irwin_std",
    "irwin_min",
    "irwin_p10",
    "irwin_p25",
    "irwin_p50",
    "irwin_p75",
    "irwin_max",
    "irwin_temp_range",
    "irwin_cold_cloud_fraction_233k",
    "irwin_very_cold_cloud_fraction_219k",
    "irwin_overshooting_fraction_203k",
    # Family B: Core / Ring Structural Proxies (11)
    "irwin_core_mean",
    "irwin_core_min",
    "irwin_core_cold_frac",
    "irwin_core_very_cold_frac",
    "irwin_ring_mean",
    "irwin_ring_min",
    "irwin_ring_cold_frac",
    "irwin_outer_mean",
    "irwin_core_ring_diff",
    "irwin_core_outer_diff",
    "irwin_azimuthal_std_core",
    # Family C: Spatial Texture & Gradients (4)
    "irwin_grad_mean",
    "irwin_grad_max",
    "irwin_local_variance",
    "irwin_spatial_entropy",
    # Family D: Multispectral IR/WV (7)
    "has_irwvp",
    "irwvp_mean",
    "irwvp_min",
    "irwvp_core_mean",
    "ir_wv_diff_mean",
    "ir_wv_core_diff",
    "ir_wv_spatial_corr",
    # Family E: Visible Channel (4)
    "has_vschn",
    "vschn_mean",
    "vschn_core_mean",
    "vschn_std",
)

# Canonical 23 temporal features matching Sprint 6 subset_b
TEMPORAL_FEATURE_NAMES: Tuple[str, ...] = (
    "track_latitude_val",
    "track_latitude_is_observed",
    "track_longitude_val",
    "track_longitude_is_observed",
    "track_wind_speed_val",
    "track_wind_speed_is_observed",
    "track_pressure_val",
    "track_pressure_is_observed",
    "track_translation_speed_kts_val",
    "track_translation_speed_kts_is_observed",
    "track_translation_bearing_deg_val",
    "track_translation_bearing_deg_is_observed",
    "temp_delta_wind_6h_val",
    "temp_delta_wind_6h_is_observed",
    "temp_delta_wind_12h_val",
    "temp_delta_wind_12h_is_observed",
    "temp_delta_pressure_6h_val",
    "temp_delta_pressure_6h_is_observed",
    "temp_wind_change_rate_per_hour_val",
    "temp_wind_change_rate_per_hour_is_observed",
    "temp_delta_ir_min_6h_val",
    "temp_delta_ir_min_6h_is_observed",
    "quality_track_available",
)


@dataclass
class SpatialSample:
    """
    A single observation fix containing spatial satellite features,
    temporal kinematic features, provenance metadata, and forward RI target.
    """
    storm_id: str
    storm_name: str
    observation_time: str
    partition: str
    spatial_features: Dict[str, float]
    source_availability: Dict[str, float]
    quality_flags: List[str]
    ri_target: Optional[int]
    horizon: float = 24.0
    
    # Kinematic & temporal context
    latitude: float = 0.0
    longitude: float = 0.0
    current_wind_kts: Optional[float] = None
    future_wind_kts: Optional[float] = None
    delta_wind_kts: Optional[float] = None
    ri_label_status: str = "AVAILABLE"
    is_supervised: bool = True
    temporal_features: Optional[Dict[str, float]] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "storm_id": self.storm_id,
            "storm_name": self.storm_name,
            "observation_time": self.observation_time,
            "partition": self.partition,
            "horizon": self.horizon,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "current_wind_kts": self.current_wind_kts,
            "future_wind_kts": self.future_wind_kts,
            "delta_wind_kts": self.delta_wind_kts,
            "ri_label_status": self.ri_label_status,
            "is_supervised": self.is_supervised,
            "ri_target": self.ri_target,
            "quality_flags": ";".join(self.quality_flags),
        }
        d.update(self.source_availability)
        d.update(self.spatial_features)
        if self.temporal_features:
            d.update(self.temporal_features)
        return d


class SpatialRIDataset:
    """
    Container for SpatialSample objects with partition filtering,
    NumPy matrix exports, and statistical summaries.
    """

    def __init__(self, samples: List[SpatialSample]):
        self.samples = samples

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> SpatialSample:
        return self.samples[idx]

    def get_supervised_samples(self) -> List[SpatialSample]:
        """Returns samples with valid, non-null RI ground truth."""
        return [s for s in self.samples if s.is_supervised and s.ri_target is not None]

    def filter_by_partition(self, partition: str) -> "SpatialRIDataset":
        """Filter dataset by partition name ('TRAIN', 'VAL', 'TEST')."""
        return SpatialRIDataset([s for s in self.samples if s.partition.upper() == partition.upper()])

    def filter_by_storm_ids(self, storm_ids: Set[str]) -> "SpatialRIDataset":
        """Filter dataset by set of storm identifiers."""
        return SpatialRIDataset([s for s in self.samples if s.storm_id in storm_ids])

    def to_dataframe(self, supervised_only: bool = False) -> pd.DataFrame:
        """Converts dataset to a flat pandas DataFrame."""
        items = self.get_supervised_samples() if supervised_only else self.samples
        records = [s.to_dict() for s in items]
        return pd.DataFrame(records)

    def to_numpy(
        self,
        feature_names: Optional[List[str]] = None,
        supervised_only: bool = True,
        include_temporal: bool = False,
    ) -> Tuple[np.ndarray, np.ndarray, List[Dict[str, Any]]]:
        """
        Exports feature matrix X, target vector y, and metadata rows.

        Args:
            feature_names: Explicit list of feature names to extract.
                           Defaults to all 38 spatial features.
            supervised_only: If True, returns only samples with valid ri_target.
            include_temporal: If True and feature_names is None, combines
                              Sprint 6 temporal (23) + Sprint 9 spatial (38).

        Returns:
            X: 2D numpy array of shape (N, D), dtype float32
            y: 1D numpy array of shape (N,), dtype int64
            metadata: List of metadata dicts per observation
        """
        samples = self.get_supervised_samples() if supervised_only else self.samples
        if not samples:
            return np.empty((0, 0), dtype=np.float32), np.empty((0,), dtype=np.int64), []

        if feature_names is None:
            if include_temporal:
                feature_names = list(TEMPORAL_FEATURE_NAMES) + list(SPATIAL_FEATURE_NAMES)
            else:
                feature_names = list(SPATIAL_FEATURE_NAMES)

        X_rows = []
        y_rows = []
        meta_rows = []

        for s in samples:
            row_dict = {}
            row_dict.update(s.spatial_features)
            row_dict.update(s.source_availability)
            if s.temporal_features:
                row_dict.update(s.temporal_features)

            vals = [float(row_dict.get(fname, np.nan)) for fname in feature_names]
            X_rows.append(vals)
            y_rows.append(int(s.ri_target) if s.ri_target is not None else -1)
            meta_rows.append({
                "storm_id": s.storm_id,
                "storm_name": s.storm_name,
                "observation_time": s.observation_time,
                "partition": s.partition,
                "ri_target": s.ri_target,
                "delta_wind_kts": s.delta_wind_kts,
            })

        X = np.array(X_rows, dtype=np.float32)
        y = np.array(y_rows, dtype=np.int64)
        return X, y, meta_rows


class SpatialRIDatasetBuilder:
    """
    Builds the spatial dataset by extracting features from NetCDF/NumPy patches
    and matching with verified ground truth from Sprint 8.
    """

    def __init__(
        self,
        config: Optional[SpatialFeatureConfig] = None,
        project_root: Optional[str] = None,
    ):
        self.config = config or SpatialFeatureConfig()
        self.extractor = SatelliteSpatialFeatureExtractor(self.config)
        self.project_root = project_root or os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )

    def build(
        self,
        ri_samples_csv: Optional[str] = None,
        patches_root: Optional[str] = None,
    ) -> SpatialRIDataset:
        """
        Builds the complete spatial dataset.
        """
        csv_path = ri_samples_csv or os.path.join(
            self.project_root, "data", "processed", "hursat_ri_samples.csv"
        )
        p_root = patches_root or os.path.join(
            self.project_root, "data", "processed", "satellite_patches"
        )

        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Verified RI samples CSV not found at: {csv_path}")

        df = pd.read_csv(csv_path)

        # Precompute temporal features per storm sequence to ensure causal continuity
        temporal_by_storm_time: Dict[Tuple[str, str], Dict[str, float]] = {}
        for storm_id, grp in df.groupby("storm_id"):
            grp_sorted = grp.sort_values("cyclone_time_utc").to_dict("records")
            for i, curr in enumerate(grp_sorted):
                t_curr = curr["cyclone_time_utc"]
                p_curr = CycloneTrackPoint(
                    storm_id=storm_id,
                    storm_name=curr["storm_name"],
                    season=int(t_curr[:4]),
                    basin="NI",
                    timestamp_utc=t_curr,
                    latitude=float(curr["latitude"]),
                    longitude=float(curr["longitude"]),
                    wind_speed_kts=float(curr["current_wind_kts"]) if pd.notna(curr["current_wind_kts"]) else None,
                    central_pressure_mb=float(curr["central_pressure_mb"]) if pd.notna(curr["central_pressure_mb"]) else None,
                    nature=curr["nature"] if pd.notna(curr["nature"]) else "TS",
                )

                # Previous point for translation speed/bearing
                p_prev = None
                if i > 0:
                    prev = grp_sorted[i - 1]
                    p_prev = CycloneTrackPoint(
                        storm_id=storm_id,
                        storm_name=prev["storm_name"],
                        season=int(prev["cyclone_time_utc"][:4]),
                        basin="NI",
                        timestamp_utc=prev["cyclone_time_utc"],
                        latitude=float(prev["latitude"]),
                        longitude=float(prev["longitude"]),
                        wind_speed_kts=float(prev["current_wind_kts"]) if pd.notna(prev["current_wind_kts"]) else None,
                        central_pressure_mb=float(prev["central_pressure_mb"]) if pd.notna(prev["central_pressure_mb"]) else None,
                        nature=prev["nature"] if pd.notna(prev["nature"]) else "TS",
                    )

                track_feats = TrackFeatureExtractor.extract(p_curr, p_prev)

                # Find 6h and 12h historical points
                dt_curr = datetime.fromisoformat(t_curr.replace("Z", "+00:00"))
                h6_row, h12_row = None, None
                for j in range(i - 1, -1, -1):
                    t_past = datetime.fromisoformat(grp_sorted[j]["cyclone_time_utc"].replace("Z", "+00:00"))
                    diff_h = (dt_curr - t_past).total_seconds() / 3600.0
                    if h6_row is None and 4.0 <= diff_h <= 8.5:
                        h6_row = grp_sorted[j]
                    if h12_row is None and 10.0 <= diff_h <= 15.0:
                        h12_row = grp_sorted[j]
                    if diff_h > 16.0:
                        break

                t_6h_time = h6_row["cyclone_time_utc"] if h6_row else None
                t_6h_wind = float(h6_row["current_wind_kts"]) if (h6_row and pd.notna(h6_row["current_wind_kts"])) else None
                t_6h_pres = float(h6_row["central_pressure_mb"]) if (h6_row and pd.notna(h6_row["central_pressure_mb"])) else None

                t_12h_time = h12_row["cyclone_time_utc"] if h12_row else None
                t_12h_wind = float(h12_row["current_wind_kts"]) if (h12_row and pd.notna(h12_row["current_wind_kts"])) else None

                temp_feats = TemporalFeatureExtractor.extract(
                    current_time_utc=t_curr,
                    current_wind_kts=p_curr.wind_speed_kts,
                    current_pressure_mb=p_curr.central_pressure_mb,
                    hist_6h_time_utc=t_6h_time,
                    hist_6h_wind_kts=t_6h_wind,
                    hist_6h_pressure_mb=t_6h_pres,
                    hist_12h_time_utc=t_12h_time,
                    hist_12h_wind_kts=t_12h_wind,
                )

                # Format exact 23 Sprint 6 features
                t_dict = {
                    "track_latitude_val": float(track_feats["track_latitude"]) if track_feats["track_latitude"] is not None else 0.0,
                    "track_latitude_is_observed": 1.0 if track_feats["track_latitude"] is not None else 0.0,
                    "track_longitude_val": float(track_feats["track_longitude"]) if track_feats["track_longitude"] is not None else 0.0,
                    "track_longitude_is_observed": 1.0 if track_feats["track_longitude"] is not None else 0.0,
                    "track_wind_speed_val": float(track_feats["track_wind_speed"]) if track_feats["track_wind_speed"] is not None else 0.0,
                    "track_wind_speed_is_observed": 1.0 if track_feats["track_wind_speed"] is not None else 0.0,
                    "track_pressure_val": float(track_feats["track_pressure"]) if track_feats["track_pressure"] is not None else 0.0,
                    "track_pressure_is_observed": 1.0 if track_feats["track_pressure"] is not None else 0.0,
                    "track_translation_speed_kts_val": float(track_feats["track_translation_speed_kts"]) if track_feats["track_translation_speed_kts"] is not None else 0.0,
                    "track_translation_speed_kts_is_observed": 1.0 if track_feats["track_translation_speed_kts"] is not None else 0.0,
                    "track_translation_bearing_deg_val": float(track_feats["track_translation_bearing_deg"]) if track_feats["track_translation_bearing_deg"] is not None else 0.0,
                    "track_translation_bearing_deg_is_observed": 1.0 if track_feats["track_translation_bearing_deg"] is not None else 0.0,
                    "temp_delta_wind_6h_val": float(temp_feats["temp_delta_wind_6h"]) if temp_feats["temp_delta_wind_6h"] is not None else 0.0,
                    "temp_delta_wind_6h_is_observed": 1.0 if temp_feats["temp_delta_wind_6h"] is not None else 0.0,
                    "temp_delta_wind_12h_val": float(temp_feats["temp_delta_wind_12h"]) if temp_feats["temp_delta_wind_12h"] is not None else 0.0,
                    "temp_delta_wind_12h_is_observed": 1.0 if temp_feats["temp_delta_wind_12h"] is not None else 0.0,
                    "temp_delta_pressure_6h_val": float(temp_feats["temp_delta_pressure_6h"]) if temp_feats["temp_delta_pressure_6h"] is not None else 0.0,
                    "temp_delta_pressure_6h_is_observed": 1.0 if temp_feats["temp_delta_pressure_6h"] is not None else 0.0,
                    "temp_wind_change_rate_per_hour_val": float(temp_feats["temp_wind_change_rate_per_hour"]) if temp_feats["temp_wind_change_rate_per_hour"] is not None else 0.0,
                    "temp_wind_change_rate_per_hour_is_observed": 1.0 if temp_feats["temp_wind_change_rate_per_hour"] is not None else 0.0,
                    "temp_delta_ir_min_6h_val": 0.0,
                    "temp_delta_ir_min_6h_is_observed": 0.0,
                    "quality_track_available": 1.0,
                }
                temporal_by_storm_time[(storm_id, t_curr)] = t_dict

        # Process each row into a SpatialSample
        samples: List[SpatialSample] = []
        for _, row in df.iterrows():
            storm_id = str(row["storm_id"])
            storm_name = str(row["storm_name"])
            t_curr = str(row["cyclone_time_utc"])
            partition = str(row["partition"])
            patch_dir = os.path.join(self.project_root, str(row["patch_dir"])) if not os.path.isabs(str(row["patch_dir"])) else str(row["patch_dir"])

            irwin_path = os.path.join(patch_dir, "IRWIN", "patch.npy")
            irwvp_path = os.path.join(patch_dir, "IRWVP", "patch.npy")
            vschn_path = os.path.join(patch_dir, "VSCHN", "patch.npy")

            irwin = np.load(irwin_path) if os.path.exists(irwin_path) else None
            irwvp = np.load(irwvp_path) if os.path.exists(irwvp_path) else None
            vschn = np.load(vschn_path) if os.path.exists(vschn_path) else None

            if irwin is None:
                continue

            spatial_feats = self.extractor.extract_all_features(
                irwin_patch=irwin,
                irwvp_patch=irwvp,
                vschn_patch=vschn,
            )

            source_avail = {
                "has_irwin": 1.0,
                "has_irwvp": float(spatial_feats.get("has_irwvp", 0.0)),
                "has_vschn": float(spatial_feats.get("has_vschn", 0.0)),
            }

            quality_flags = [str(row["ir_quality"])] if pd.notna(row.get("ir_quality")) else []

            is_avail = (row["ri_label_status"] == "AVAILABLE") and pd.notna(row["ri_target"])
            ri_target = int(float(row["ri_target"])) if is_avail else None

            sample = SpatialSample(
                storm_id=storm_id,
                storm_name=storm_name,
                observation_time=t_curr,
                partition=partition,
                spatial_features=spatial_feats,
                source_availability=source_avail,
                quality_flags=quality_flags,
                ri_target=ri_target,
                horizon=float(row.get("ri_horizon_hours", 24.0)),
                latitude=float(row.get("latitude", 0.0)),
                longitude=float(row.get("longitude", 0.0)),
                current_wind_kts=float(row["current_wind_kts"]) if pd.notna(row.get("current_wind_kts")) else None,
                future_wind_kts=float(row["future_wind_kts"]) if pd.notna(row.get("future_wind_kts")) else None,
                delta_wind_kts=float(row["delta_wind_kts"]) if pd.notna(row.get("delta_wind_kts")) else None,
                ri_label_status=str(row["ri_label_status"]),
                is_supervised=is_avail,
                temporal_features=temporal_by_storm_time.get((storm_id, t_curr)),
            )
            samples.append(sample)

        return SpatialRIDataset(samples)
