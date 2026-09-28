"""
CycloneGuard Track Feature Extraction.

Extracts kinematic and intensity features from verified best-track series:
- Instantaneous center location
- Maximum sustained wind speed & minimum central pressure
- Forward translation speed (knots) via great-circle distance
- Compass bearing of cyclone forward motion
"""

from datetime import datetime
import math
from typing import Any, Dict, Optional
from ml.data.schemas.track import CycloneTrackPoint, CycloneTrackSeries


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points on Earth in kilometers."""
    r_earth = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r_earth * c


def calculate_bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the initial compass bearing from point 1 to point 2 (0-360 degrees)."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_lambda = math.radians(lon2 - lon1)

    y = math.sin(delta_lambda) * math.cos(phi2)
    x = (math.cos(phi1) * math.sin(phi2) -
         math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda))
    bearing = math.degrees(math.atan2(y, x))
    return (bearing + 360.0) % 360.0


class TrackFeatureExtractor:
    """
    Extracts structured track features for a specific track point within a track series.
    """
    @staticmethod
    def extract(
        current_point: CycloneTrackPoint,
        previous_point: Optional[CycloneTrackPoint] = None,
    ) -> Dict[str, Any]:
        """
        Extract track features for the current point, calculating motion kinematics
        if a valid previous point is provided.
        """
        features: Dict[str, Any] = {
            "track_latitude": current_point.latitude,
            "track_longitude": current_point.longitude,
            "track_wind_speed": current_point.wind_speed_kts,
            "track_pressure": current_point.central_pressure_mb,
            "track_translation_speed_kts": None,
            "track_translation_bearing_deg": None,
        }

        if previous_point is not None:
            t_curr = datetime.fromisoformat(str(current_point.timestamp_utc).replace("Z", "+00:00"))
            t_prev = datetime.fromisoformat(str(previous_point.timestamp_utc).replace("Z", "+00:00"))
            time_diff_hours = (t_curr - t_prev).total_seconds() / 3600.0

            if 1.0 <= time_diff_hours <= 12.0:
                dist_km = haversine_distance_km(
                    previous_point.latitude,
                    previous_point.longitude,
                    current_point.latitude,
                    current_point.longitude,
                )
                # 1 km = 0.539957 nautical miles
                speed_kts = (dist_km * 0.539957) / time_diff_hours
                bearing_deg = calculate_bearing_deg(
                    previous_point.latitude,
                    previous_point.longitude,
                    current_point.latitude,
                    current_point.longitude,
                )
                features["track_translation_speed_kts"] = round(speed_kts, 2)
                features["track_translation_bearing_deg"] = round(bearing_deg, 2)

        return features
