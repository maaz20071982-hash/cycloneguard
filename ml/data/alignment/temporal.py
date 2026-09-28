"""
Temporal Alignment Engine for CycloneGuard.
Matches satellite observation timestamps to cyclone best-track trajectories with explicit tolerance limits.
Records exact time differences and never silently pairs distant observations.
"""

from datetime import datetime, timezone
from typing import List, Optional, Tuple
from pydantic import BaseModel

from ml.data.schemas.track import CycloneTrackPoint, CycloneTrackSeries


class TemporalAlignmentResult(BaseModel):
    satellite_time_utc: str
    matched_track_time_utc: str
    time_difference_seconds: float
    time_difference_hours: float
    matched_latitude: float
    matched_longitude: float
    matched_wind_kts: Optional[float] = None
    matched_pressure_mb: Optional[float] = None
    is_interpolated: bool = False
    is_within_tolerance: bool = True
    tolerance_threshold_hours: float


class TemporalAligner:
    """Aligns observational timestamps with cyclone track trajectories."""

    @staticmethod
    def align_observation_to_track(
        satellite_time_str: str,
        track: CycloneTrackSeries,
        max_tolerance_hours: float = 3.0,
        interpolate_position: bool = True,
    ) -> Optional[TemporalAlignmentResult]:
        """
        Finds the closest track point in time to the satellite observation.
        If interpolate_position is True and the observation falls strictly between two track points,
        linearly interpolates latitude and longitude.
        If the closest point is beyond max_tolerance_hours, returns result with is_within_tolerance=False.
        """
        if not track.points:
            return None

        sat_dt = datetime.fromisoformat(satellite_time_str.replace("Z", "+00:00"))
        sat_epoch = sat_dt.timestamp()

        # Parse track point timestamps
        point_epochs: List[Tuple[float, CycloneTrackPoint]] = []
        for p in track.points:
            p_dt = datetime.fromisoformat(p.timestamp_utc.replace("Z", "+00:00"))
            point_epochs.append((p_dt.timestamp(), p))

        point_epochs.sort(key=lambda x: x[0])

        # Find closest point
        closest_diff = float("inf")
        closest_idx = 0
        for i, (t_epoch, pt) in enumerate(point_epochs):
            diff = abs(sat_epoch - t_epoch)
            if diff < closest_diff:
                closest_diff = diff
                closest_idx = i

        diff_seconds = sat_epoch - point_epochs[closest_idx][0]
        diff_hours = abs(diff_seconds) / 3600.0
        is_within_tol = diff_hours <= max_tolerance_hours

        # Attempt linear interpolation if between two points and requested
        interpolated = False
        interp_lat = point_epochs[closest_idx][1].latitude
        interp_lon = point_epochs[closest_idx][1].longitude
        matched_time = point_epochs[closest_idx][1].timestamp_utc
        matched_wind = point_epochs[closest_idx][1].wind_speed_kts
        matched_pres = point_epochs[closest_idx][1].central_pressure_mb

        if interpolate_position and is_within_tol and len(point_epochs) > 1:
            for i in range(len(point_epochs) - 1):
                t1, p1 = point_epochs[i]
                t2, p2 = point_epochs[i + 1]
                if t1 <= sat_epoch <= t2 and (t2 - t1) > 0:
                    alpha = (sat_epoch - t1) / (t2 - t1)
                    interp_lat = round(p1.latitude + alpha * (p2.latitude - p1.latitude), 4)
                    interp_lon = round(p1.longitude + alpha * (p2.longitude - p1.longitude), 4)
                    interpolated = True
                    matched_time = satellite_time_str
                    if p1.wind_speed_kts is not None and p2.wind_speed_kts is not None:
                        matched_wind = round(p1.wind_speed_kts + alpha * (p2.wind_speed_kts - p1.wind_speed_kts), 1)
                    if p1.central_pressure_mb is not None and p2.central_pressure_mb is not None:
                        matched_pres = round(p1.central_pressure_mb + alpha * (p2.central_pressure_mb - p1.central_pressure_mb), 1)
                    break

        return TemporalAlignmentResult(
            satellite_time_utc=satellite_time_str,
            matched_track_time_utc=matched_time,
            time_difference_seconds=round(diff_seconds, 2),
            time_difference_hours=round(diff_hours, 3),
            matched_latitude=interp_lat,
            matched_longitude=interp_lon,
            matched_wind_kts=matched_wind,
            matched_pressure_mb=matched_pres,
            is_interpolated=interpolated,
            is_within_tolerance=is_within_tol,
            tolerance_threshold_hours=max_tolerance_hours,
        )
