"""
CycloneGuard Temporal Feature Extraction.

Extracts dynamic rate-of-change and delta features across historical time steps:
- Delta intensity (6-hour and 12-hour wind speed change)
- Delta central pressure (6-hour pressure change)
- Instantaneous hourly rates of change
- Delta cloud-top minimum brightness temperature
"""

from typing import Any, Dict, Optional
from datetime import datetime


def _to_dt(val: Any) -> Optional[datetime]:
    if val is None:
        return None
    if isinstance(val, datetime):
        return val
    return datetime.fromisoformat(str(val).replace("Z", "+00:00"))


class TemporalFeatureExtractor:
    """
    Computes temporal derivatives across sequential cyclone states or track points.
    Strictly verifies time intervals without assuming equidistant intervals.
    """

    @classmethod
    def extract(
        cls,
        current_time_utc: Any,
        current_wind_kts: Optional[float],
        current_pressure_mb: Optional[float],
        current_ir_min_k: Optional[float] = None,
        hist_6h_time_utc: Optional[Any] = None,
        hist_6h_wind_kts: Optional[float] = None,
        hist_6h_pressure_mb: Optional[float] = None,
        hist_6h_ir_min_k: Optional[float] = None,
        hist_12h_time_utc: Optional[Any] = None,
        hist_12h_wind_kts: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Compute temporal change features given current and historical values.
        """
        features: Dict[str, Any] = {
            "temp_delta_wind_6h": None,
            "temp_delta_wind_12h": None,
            "temp_delta_pressure_6h": None,
            "temp_wind_change_rate_per_hour": None,
            "temp_delta_ir_min_6h": None,
        }

        t_curr = _to_dt(current_time_utc)
        t_6h = _to_dt(hist_6h_time_utc)
        t_12h = _to_dt(hist_12h_time_utc)

        # 6-hour window evaluation (valid within 4 to 8.5 hours)
        if t_curr is not None and t_6h is not None:
            dt_6h_hours = (t_curr - t_6h).total_seconds() / 3600.0
            if 4.0 <= dt_6h_hours <= 8.5:
                if current_wind_kts is not None and hist_6h_wind_kts is not None:
                    delta_v = current_wind_kts - hist_6h_wind_kts
                    features["temp_delta_wind_6h"] = round(delta_v, 2)
                    features["temp_wind_change_rate_per_hour"] = round(delta_v / dt_6h_hours, 3)

                if current_pressure_mb is not None and hist_6h_pressure_mb is not None:
                    delta_p = current_pressure_mb - hist_6h_pressure_mb
                    features["temp_delta_pressure_6h"] = round(delta_p, 2)

                if current_ir_min_k is not None and hist_6h_ir_min_k is not None:
                    delta_ir = current_ir_min_k - hist_6h_ir_min_k
                    features["temp_delta_ir_min_6h"] = round(delta_ir, 2)

        # 12-hour window evaluation (valid within 10 to 15 hours)
        if t_curr is not None and t_12h is not None:
            dt_12h_hours = (t_curr - t_12h).total_seconds() / 3600.0
            if 10.0 <= dt_12h_hours <= 15.0:
                if current_wind_kts is not None and hist_12h_wind_kts is not None:
                    features["temp_delta_wind_12h"] = round(current_wind_kts - hist_12h_wind_kts, 2)

        return features
