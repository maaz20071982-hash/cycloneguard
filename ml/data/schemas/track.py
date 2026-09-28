"""
Cyclone track observation schema for normalized best-track data.
Compatible with NOAA IBTrACS, IMD RSMC New Delhi, and JTWC best-track datasets.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class CycloneTrackPoint(BaseModel):
    storm_id: str
    storm_name: str
    season: int
    basin: str
    subbasin: Optional[str] = None
    timestamp_utc: str
    latitude: float
    longitude: float
    nature: Optional[str] = None
    wind_speed_kts: Optional[float] = None
    central_pressure_mb: Optional[float] = None
    agency_wind_kts: Optional[float] = None
    agency_pressure_mb: Optional[float] = None
    agency_grade: Optional[str] = None
    dist2land_km: Optional[float] = None
    landfall: Optional[bool] = None
    is_interpolated: bool = False
    raw_source: str = "ibtracs"


class CycloneTrackSeries(BaseModel):
    storm_id: str
    storm_name: str
    season: int
    basin: str
    points: List[CycloneTrackPoint] = Field(default_factory=list)

    @property
    def start_time(self) -> Optional[str]:
        return self.points[0].timestamp_utc if self.points else None

    @property
    def end_time(self) -> Optional[str]:
        return self.points[-1].timestamp_utc if self.points else None

    @property
    def peak_wind_kts(self) -> Optional[float]:
        winds = [p.wind_speed_kts for p in self.points if p.wind_speed_kts is not None]
        return max(winds) if winds else None

    @property
    def min_pressure_mb(self) -> Optional[float]:
        pressures = [p.central_pressure_mb for p in self.points if p.central_pressure_mb is not None]
        return min(pressures) if pressures else None
