"""
Temporal Sequence Builder for CycloneGuard.
Constructs multi-timestep observation sequences adapting to actual available timestamps.
Never forces missing frames or interpolates fake satellite observations.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from ml.data.schemas.track import CycloneTrackPoint, CycloneTrackSeries
from ml.data.sequences.ri_label import RILabelGenerator, RILabelResult


class SequenceFrame(BaseModel):
    timestamp_utc: str
    relative_hours: float
    time_difference_to_nominal_hours: float
    observation_metadata: Dict[str, Any] = Field(default_factory=dict)


class TemporalSequence(BaseModel):
    storm_id: str
    storm_name: Optional[str] = None
    reference_time_utc: str  # t0
    target_relative_hours: List[float]  # e.g. [-12.0, -6.0, -3.0, 0.0]
    frames: List[SequenceFrame] = Field(default_factory=list)
    is_complete: bool = False
    current_wind_kts: Optional[float] = None
    current_pressure_mb: Optional[float] = None
    future_wind_kts: Optional[float] = None
    ri_label: Optional[RILabelResult] = None
    channels: List[str] = Field(default_factory=list)
    source_id: str = "hursat"


class TemporalSequenceBuilder:
    """Builds temporal sequence windows from available observational timestamps."""

    @staticmethod
    def build_sequence(
        t0_point: CycloneTrackPoint,
        track_series: CycloneTrackSeries,
        relative_offsets_hours: Optional[List[float]] = None,
        tolerance_hours: float = 1.5,
        compute_ri_label: bool = True,
        ri_horizon_hours: float = 24.0,
        ri_threshold_kts: float = 30.0,
    ) -> TemporalSequence:
        """
        Builds an adaptive temporal sequence centered on t0_point.
        Default relative offsets: [-12.0, -6.0, -3.0, 0.0] hours.
        """
        if relative_offsets_hours is None:
            relative_offsets_hours = [-12.0, -6.0, -3.0, 0.0]

        t0_dt = datetime.fromisoformat(t0_point.timestamp_utc.replace("Z", "+00:00"))
        t0_epoch = t0_dt.timestamp()

        # Index track points by epoch
        track_epochs = [
            (datetime.fromisoformat(p.timestamp_utc.replace("Z", "+00:00")).timestamp(), p)
            for p in track_series.points
        ]
        track_epochs.sort(key=lambda x: x[0])

        frames = []
        is_complete = True

        for offset in relative_offsets_hours:
            target_epoch = t0_epoch + offset * 3600.0

            # Find closest observation
            best_diff = float("inf")
            best_p = None
            for epoch_p, p in track_epochs:
                diff_h = abs(epoch_p - target_epoch) / 3600.0
                if diff_h < best_diff:
                    best_diff = diff_h
                    best_p = p

            if best_p is not None and best_diff <= tolerance_hours:
                frames.append(SequenceFrame(
                    timestamp_utc=best_p.timestamp_utc,
                    relative_hours=offset,
                    time_difference_to_nominal_hours=round(best_diff, 2),
                    observation_metadata={
                        "lat": best_p.latitude,
                        "lon": best_p.longitude,
                        "wind_kts": best_p.wind_speed_kts,
                        "pres_mb": best_p.central_pressure_mb,
                    },
                ))
            else:
                is_complete = False

        ri_res = None
        if compute_ri_label:
            ri_res = RILabelGenerator.generate_label(
                current_point=t0_point,
                track_series=track_series,
                horizon_hours=ri_horizon_hours,
                threshold_kts=ri_threshold_kts,
            )

        return TemporalSequence(
            storm_id=t0_point.storm_id,
            storm_name=t0_point.storm_name,
            reference_time_utc=t0_point.timestamp_utc,
            target_relative_hours=relative_offsets_hours,
            frames=frames,
            is_complete=is_complete,
            current_wind_kts=t0_point.wind_speed_kts,
            current_pressure_mb=t0_point.central_pressure_mb,
            future_wind_kts=ri_res.future_wind_kts if ri_res else None,
            ri_label=ri_res,
        )
