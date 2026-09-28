"""
Rapid Intensification (RI) Label Generation Foundation for CycloneGuard.
Implements meteorologically grounded, configurable Rapid Intensification labeling:
- Standard WMO/NHC Operational Definition: delta_wind >= 30 knots in <= 24 hours.
- Configurable forecast horizons (e.g. 12h, 24h, 36h) and delta thresholds.
- Scientific Rule: If future observation at t + horizon is unavailable, mark label as UNAVAILABLE (None).
  Do NOT infer, interpolate, or guess future ground truth.
"""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from ml.data.schemas.track import CycloneTrackPoint, CycloneTrackSeries


class RILabelResult(BaseModel):
    storm_id: str
    current_time_utc: str
    target_time_utc: Optional[str] = None
    horizon_hours: float
    threshold_kts: float
    current_wind_kts: Optional[float] = None
    future_wind_kts: Optional[float] = None
    delta_wind_kts: Optional[float] = None
    is_ri: Optional[bool] = None
    status: str = "AVAILABLE"  # "AVAILABLE", "UNAVAILABLE_MISSING_FUTURE", "UNAVAILABLE_MISSING_CURRENT"
    units: Dict[str, str] = Field(default_factory=lambda: {
        "wind_speed": "knots (maximum sustained)",
        "horizon": "hours",
        "threshold": "knots increase",
    })
    justification: str = ""


class RILabelGenerator:
    """Generates ground-truth Rapid Intensification labels from best-track series."""

    @staticmethod
    def generate_label(
        current_point: CycloneTrackPoint,
        track_series: CycloneTrackSeries,
        horizon_hours: float = 24.0,
        threshold_kts: float = 30.0,
        tolerance_hours: float = 3.0,
    ) -> RILabelResult:
        """
        Evaluates whether cyclone undergoes Rapid Intensification within horizon_hours.
        Looks up track observation at current_time + horizon_hours (+- tolerance_hours).
        """
        sid = current_point.storm_id
        t_curr_str = current_point.timestamp_utc
        dt_curr = datetime.fromisoformat(t_curr_str.replace("Z", "+00:00"))
        epoch_curr = dt_curr.timestamp()

        # Check current intensity availability
        v_curr = current_point.wind_speed_kts
        if v_curr is None:
            return RILabelResult(
                storm_id=sid,
                current_time_utc=t_curr_str,
                horizon_hours=horizon_hours,
                threshold_kts=threshold_kts,
                status="UNAVAILABLE_MISSING_CURRENT",
                justification="Current wind intensity is not available in best-track record.",
            )

        # Target future epoch
        target_epoch = epoch_curr + horizon_hours * 3600.0
        target_iso = datetime.fromtimestamp(target_epoch, tz=dt_curr.tzinfo).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Search for closest future point within tolerance
        closest_point: Optional[CycloneTrackPoint] = None
        closest_diff = float("inf")

        for p in track_series.points:
            dt_p = datetime.fromisoformat(p.timestamp_utc.replace("Z", "+00:00"))
            epoch_p = dt_p.timestamp()
            diff_hours = abs(epoch_p - target_epoch) / 3600.0
            if diff_hours <= tolerance_hours and diff_hours < closest_diff:
                closest_diff = diff_hours
                closest_point = p

        if closest_point is None or closest_point.wind_speed_kts is None:
            return RILabelResult(
                storm_id=sid,
                current_time_utc=t_curr_str,
                target_time_utc=target_iso,
                horizon_hours=horizon_hours,
                threshold_kts=threshold_kts,
                current_wind_kts=v_curr,
                status="UNAVAILABLE_MISSING_FUTURE",
                justification=f"No valid future observation found within {tolerance_hours}h of target time {target_iso}.",
            )

        v_future = closest_point.wind_speed_kts
        delta_v = round(v_future - v_curr, 1)
        is_ri = delta_v >= threshold_kts

        justification = (
            f"Rapid Intensification detected: +{delta_v} kts >= {threshold_kts} kts in {horizon_hours}h "
            f"({v_curr} kts at {t_curr_str} -> {v_future} kts at {closest_point.timestamp_utc})."
            if is_ri
            else f"Non-RI: +{delta_v} kts < {threshold_kts} kts in {horizon_hours}h "
            f"({v_curr} kts at {t_curr_str} -> {v_future} kts at {closest_point.timestamp_utc})."
        )

        return RILabelResult(
            storm_id=sid,
            current_time_utc=t_curr_str,
            target_time_utc=closest_point.timestamp_utc,
            horizon_hours=horizon_hours,
            threshold_kts=threshold_kts,
            current_wind_kts=v_curr,
            future_wind_kts=v_future,
            delta_wind_kts=delta_v,
            is_ri=is_ri,
            status="AVAILABLE",
            justification=justification,
        )
