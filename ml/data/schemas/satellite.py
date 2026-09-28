"""
Satellite observation and cyclone-centered crop schemas.
"""

from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field, ConfigDict


class SatelliteMetadata(BaseModel):
    source_id: str
    satellite_name: str
    timestamp_utc: str
    channels: List[str] = Field(default_factory=list)
    units: Dict[str, str] = Field(default_factory=dict)
    grid_shape: Tuple[int, int]
    lat_bounds: Tuple[float, float]
    lon_bounds: Tuple[float, float]
    spatial_resolution_km: Optional[float] = None
    missing_value_flags: List[float] = Field(default_factory=list)


class CycloneCenteredCrop(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    storm_id: str
    storm_name: Optional[str] = None
    observation_time_utc: str
    track_time_utc: str
    center_latitude: float
    center_longitude: float
    crop_height: int
    crop_width: int
    pixel_resolution_deg: float
    channels: List[str] = Field(default_factory=list)
    source_id: str
    time_difference_seconds: float
    is_boundary_padded: bool = False
    missing_pixels_count: int = 0
    missing_pixels_fraction: float = 0.0
    quality_flag: str = "NOMINAL"
    array_shape: Tuple[int, ...]
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    mean_value: Optional[float] = None
    crop_array: Optional[Any] = None
