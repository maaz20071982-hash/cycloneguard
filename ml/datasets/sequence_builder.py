"""
CycloneGuard Temporal Sequence & Future Target Builder.

Assembles multi-step temporal state sequences (t-12h, t-6h, t-3h, t0) for time-series modeling
and prepares future intensity targets and Rapid Intensification labels with zero lookahead leakage.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import yaml
import numpy as np

from ml.data.schemas.track import CycloneTrackPoint, CycloneTrackSeries
from ml.features.cyclone_state import CycloneState
from ml.features.state_encoder import CycloneStateEncoder


@dataclass
class CycloneStateSequence:
    """
    Temporal sequence of cyclone states leading up to observation time t0,
    paired with verified future targets for supervised modeling.
    """
    storm_id: str
    storm_name: Optional[str]
    t0_time_utc: str
    sequence_length: int
    timestamps_utc: List[str]
    state_matrix: np.ndarray  # Shape: (T, feature_dim)
    
    # Ground-truth targets at t0 (evaluated only on actual future observations)
    current_intensity_kts: Optional[float] = None
    future_intensity_12h_kts: Optional[float] = None
    future_intensity_24h_kts: Optional[float] = None
    future_intensity_36h_kts: Optional[float] = None
    delta_intensity_12h_kts: Optional[float] = None
    delta_intensity_24h_kts: Optional[float] = None
    ri_label_24h: Optional[int] = None  # 1 = RI, 0 = Non-RI, None = Unavailable
    
    # Quality and provenance
    quality_flags: List[str] = field(default_factory=list)
    has_valid_ri_label: bool = False


class SequenceBuilder:
    """
    Builds temporal state sequences and computes future targets from verified tracks.
    """

    def __init__(
        self,
        encoder: Optional[CycloneStateEncoder] = None,
        ri_threshold_kts: float = 30.0,
        forecast_horizon_hours: float = 24.0,
    ):
        self.encoder = encoder or CycloneStateEncoder()
        self.ri_threshold_kts = ri_threshold_kts
        self.forecast_horizon_hours = forecast_horizon_hours

    @classmethod
    def from_config_file(cls, config_path: str, encoder: Optional[CycloneStateEncoder] = None) -> "SequenceBuilder":
        """Initialize from ri_config.yaml."""
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)

        thresh = float(cfg.get("threshold", {}).get("value", 30.0))
        horizon = float(cfg.get("threshold", {}).get("forecast_horizon_hours", 24.0))
        return cls(encoder=encoder, ri_threshold_kts=thresh, forecast_horizon_hours=horizon)

    def build_sequence_for_point(
        self,
        current_state: CycloneState,
        track_series: CycloneTrackSeries,
        history_states: Optional[List[CycloneState]] = None,
        nominal_lookback_hours: List[float] = None,
    ) -> CycloneStateSequence:
        """
        Assemble a sequence of historical states ending at current_state (t0),
        and lookup future ground-truth targets strictly from future track points.
        """
        if nominal_lookback_hours is None:
            nominal_lookback_hours = [12.0, 6.0, 3.0, 0.0]

        t0_dt = datetime.fromisoformat(current_state.timestamp_utc.replace("Z", "+00:00"))

        # 1. Collect sequential states
        ordered_states: List[CycloneState] = []
        if history_states:
            # Sort history chronologically
            sorted_hist = sorted(
                history_states,
                key=lambda s: datetime.fromisoformat(s.timestamp_utc.replace("Z", "+00:00")),
            )
            for state in sorted_hist:
                s_dt = datetime.fromisoformat(state.timestamp_utc.replace("Z", "+00:00"))
                if s_dt < t0_dt:
                    ordered_states.append(state)

        ordered_states.append(current_state)

        # 2. Encode state matrix
        encoded_vectors = [self.encoder.encode(s) for s in ordered_states]
        state_matrix = np.vstack(encoded_vectors)

        # 3. Lookup future targets strictly from future track records
        # DO NOT interpolate future intensity merely to create a label.
        future_12h_pt = self._find_future_point(track_series, t0_dt, target_hours=12.0, tolerance_hours=2.0)
        future_24h_pt = self._find_future_point(track_series, t0_dt, target_hours=24.0, tolerance_hours=2.5)
        future_36h_pt = self._find_future_point(track_series, t0_dt, target_hours=36.0, tolerance_hours=3.0)

        v0 = current_state.intensity.value
        v12 = future_12h_pt.wind_speed_kts if future_12h_pt else None
        v24 = future_24h_pt.wind_speed_kts if future_24h_pt else None
        v36 = future_36h_pt.wind_speed_kts if future_36h_pt else None

        delta_12 = (v12 - v0) if (v0 is not None and v12 is not None) else None
        delta_24 = (v24 - v0) if (v0 is not None and v24 is not None) else None

        # 4. Generate Rapid Intensification (RI) label
        ri_label: Optional[int] = None
        has_valid_ri = False
        if delta_24 is not None:
            ri_label = 1 if delta_24 >= self.ri_threshold_kts else 0
            has_valid_ri = True

        timestamps = [s.timestamp_utc for s in ordered_states]
        quality_flags = [s.data_quality.get("quality_overall_flag", "UNKNOWN") for s in ordered_states]

        return CycloneStateSequence(
            storm_id=current_state.storm_id,
            storm_name=current_state.storm_name,
            t0_time_utc=current_state.timestamp_utc,
            sequence_length=len(ordered_states),
            timestamps_utc=timestamps,
            state_matrix=state_matrix,
            current_intensity_kts=v0,
            future_intensity_12h_kts=v12,
            future_intensity_24h_kts=v24,
            future_intensity_36h_kts=v36,
            delta_intensity_12h_kts=delta_12,
            delta_intensity_24h_kts=delta_24,
            ri_label_24h=ri_label,
            quality_flags=quality_flags,
            has_valid_ri_label=has_valid_ri,
        )

    @staticmethod
    def _find_future_point(
        track_series: CycloneTrackSeries,
        base_time_utc: datetime,
        target_hours: float,
        tolerance_hours: float = 2.0,
    ) -> Optional[CycloneTrackPoint]:
        """
        Locate a verified track point at approximately base_time + target_hours.
        Returns None if no observation exists within tolerance.
        """
        target_dt = base_time_utc + timedelta(hours=target_hours)
        best_pt: Optional[CycloneTrackPoint] = None
        min_diff_sec = float("inf")

        for pt in track_series.points:
            pt_dt = datetime.fromisoformat(str(pt.timestamp_utc).replace("Z", "+00:00"))
            diff_sec = abs((pt_dt - target_dt).total_seconds())
            if diff_sec <= tolerance_hours * 3600.0:
                if diff_sec < min_diff_sec:
                    min_diff_sec = diff_sec
                    best_pt = pt

        return best_pt
