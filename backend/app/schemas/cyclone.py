"""
Pydantic Schemas for Cyclone and Observation API contracts (Phase 21 & 22).
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class TrackPointResponse(BaseModel):
    timestamp: datetime
    latitude: float
    longitude: float
    wind_speed_kts: Optional[float] = None
    central_pressure_mb: Optional[float] = None
    agency_wind_kts: Optional[float] = None
    agency_grade: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CycloneResponse(BaseModel):
    id: str
    name: str
    basin: str
    international_id: Optional[str] = None
    status: str
    genesis_time: Optional[datetime] = None
    dissipation_time: Optional[datetime] = None
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CycloneDetailResponse(CycloneResponse):
    peak_wind_kts: Optional[float] = None
    min_pressure_mb: Optional[float] = None
    observation_count: int = 0


class ObservationResponse(BaseModel):
    id: str
    cyclone_id: str
    source: str
    channel: str
    observation_time: datetime
    storage_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class CycloneTrackResponse(BaseModel):
    cyclone_id: str
    name: str
    basin: str
    total_points: int
    track_points: List[TrackPointResponse] = []
