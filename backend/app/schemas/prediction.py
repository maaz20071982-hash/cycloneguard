"""
Pydantic Schemas for CycloneGuard Rapid Intensification Prediction API (Sprint 12).
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class FeatureAttributionItem(BaseModel):
    """Linear standardized feature contribution."""
    feature_name: str
    attribution_score: float
    direction: str
    model_coefficient: Optional[float] = None
    raw_value: Optional[float] = None


class EvidenceStatus(BaseModel):
    """Availability of observational evidence streams."""
    temporal_evidence_available: bool = True
    satellite_evidence_available: bool = True
    satellite_channels_available: List[str] = Field(default_factory=list)
    satellite_source: str = "NOAA HURSAT-B1 v06"
    track_source: str = "NOAA IBTrACS v04r01"


class DataProvenance(BaseModel):
    """Traceability provenance for prediction inputs."""
    track_dataset: str = "NOAA IBTrACS v04r01"
    satellite_dataset: str = "NOAA HURSAT-B1 v06"
    observation_time_utc: str
    cyclone_center_lat: float
    cyclone_center_lon: float
    temporal_match_offset_minutes: float = 0.0


class PredictionRequest(BaseModel):
    """Payload for submitting an observation for frozen model inference."""
    storm_id: str = Field(..., description="Unique storm identifier (e.g. '2015298N09062' for Chapala)")
    storm_name: Optional[str] = Field("UNNAMED", description="Designated storm name")
    observation_time_utc: Optional[str] = Field(None, description="Observation timestamp in UTC ISO-8601")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Center latitude in degrees north")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Center longitude in degrees east")
    current_wind_kts: Optional[float] = Field(None, ge=0.0, le=250.0, description="Current sustained wind speed in knots")
    wind_speed_kts: Optional[float] = Field(None, ge=0.0, le=250.0, description="Alias for current_wind_kts")
    central_pressure_mb: Optional[float] = Field(None, ge=850.0, le=1050.0, description="Minimum central pressure in mb")

    # Optional retrospective observation for temporal delta features
    prev_wind_speed_kts: Optional[float] = Field(None, ge=0.0, le=250.0, description="Wind speed 6 hours prior in knots")
    prev_latitude: Optional[float] = Field(None, ge=-90.0, le=90.0, description="Latitude 6 hours prior")
    prev_longitude: Optional[float] = Field(None, ge=-180.0, le=180.0, description="Longitude 6 hours prior")
    prev_time_utc: Optional[str] = Field(None, description="Timestamp 6 hours prior in UTC ISO-8601")

    # Pre-extracted or measured spatial features if available
    spatial_features: Optional[Dict[str, float]] = Field(None, description="Pre-extracted 38 HURSAT spatial features")
    # Retrospective track features if available
    temporal_features: Optional[Dict[str, float]] = Field(None, description="Pre-extracted 23 temporal kinematic features")

    # Threshold override (strictly for forecaster sensitivity testing)
    threshold_override: Optional[float] = Field(None, ge=0.01, le=0.99, description="Custom operational threshold")

    def model_post_init(self, __context: Any) -> None:
        if self.current_wind_kts is None and self.wind_speed_kts is not None:
            self.current_wind_kts = self.wind_speed_kts
        elif self.wind_speed_kts is None and self.current_wind_kts is not None:
            self.wind_speed_kts = self.current_wind_kts
        elif self.current_wind_kts is None and self.wind_speed_kts is None:
            self.current_wind_kts = 0.0
            self.wind_speed_kts = 0.0

        if not self.observation_time_utc:
            self.observation_time_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class PredictionResponse(BaseModel):
    """Production prediction response representing the empirical RI risk assessment."""
    prediction_id: str
    storm_id: str
    storm_name: str
    observation_time_utc: str

    model_name: str = "CycloneGuard-RI-Multimodal-TS-Final"
    model_version: str = "v3.0.0-frozen"

    ri_risk_index: float
    operating_threshold: float = 0.125
    ri_flag: bool
    risk_category: str  # LOW_RISK, ELEVATED_RISK, HIGH_RISK

    forecast_horizon_hours: float = 24.0
    ri_definition: str = "Maximum sustained 1-minute wind speed increase >= 30 kts in 24 hours"

    temporal_evidence_available: bool = True
    satellite_evidence_available: bool = True
    satellite_channels_available: List[str] = Field(default_factory=lambda: ["IRWIN", "IRWVP"])

    input_data_timestamp: str
    input_data_provenance: DataProvenance

    model_status: str = "Frozen Production Model (Sprint 11 Multi-Storm Certified)"
    calibration_status: str = "Uncalibrated Model Score (Empirical Risk Index; Platt scaling unvalidated due to sample scale)"

    top_supporting_features: List[FeatureAttributionItem] = Field(default_factory=list)
    top_suppressing_features: List[FeatureAttributionItem] = Field(default_factory=list)

    limitations: List[str] = Field(default_factory=list)
    disclaimers: List[str] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Legacy compatibility aliases
    ri_probability: Optional[float] = None
    risk_tier: Optional[str] = None
    score_interpretation: Optional[str] = None
    decision_threshold: Optional[float] = None
    contributing_features: Optional[List[Dict[str, Any]]] = None
    data_quality: Optional[str] = "NOMINAL"
    available_sources: Optional[List[str]] = None

    def model_post_init(self, __context: Any) -> None:
        if self.ri_probability is None:
            self.ri_probability = self.ri_risk_index
        if self.risk_tier is None:
            self.risk_tier = self.risk_category
        if self.decision_threshold is None:
            self.decision_threshold = self.operating_threshold
        if self.score_interpretation is None:
            self.score_interpretation = self.calibration_status
        if self.contributing_features is None:
            self.contributing_features = [
                {
                    "feature_name": item.feature_name,
                    "attribution_score": item.attribution_score,
                    "direction": item.direction,
                }
                for item in self.top_supporting_features
            ]
        if self.available_sources is None:
            self.available_sources = [
                self.input_data_provenance.track_dataset,
                self.input_data_provenance.satellite_dataset,
            ]

    model_config = ConfigDict(from_attributes=True)


class PredictionListResponse(BaseModel):
    """Paginated list of prediction records for Admin/Forecaster monitoring."""
    predictions: List[PredictionResponse]
    total: int
    skip: int = 0
    limit: int = 50
