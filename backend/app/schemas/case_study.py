"""
Pydantic Schemas for Historical Case Study & Scientific Evidence (Sprint 13).

Strict Rules:
- Never expose future outcome variables as model inputs.
- Clearly separate 'WHAT THE MODEL SAW' from 'HISTORICAL OUTCOME'.
- Label empirical scores as 'Empirical RI Risk Index', NOT 'Probability'.
- Label attribution as 'Model Feature Attribution', NOT 'Physical Cause'.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SatelliteChannelStatus(BaseModel):
    channel: str
    available: bool
    description: str
    resolution_km: float
    wavelength_microns: Optional[float] = None
    mean_tb_kelvin: Optional[float] = None
    min_tb_kelvin: Optional[float] = None


class TimelineObservationItem(BaseModel):
    """Single observation point on the historical timeline."""
    observation_id: str
    observation_time: str
    storm_id: str
    storm_name: str
    latitude: float
    longitude: float
    current_wind_kts: float
    central_pressure_mb: Optional[float] = None
    has_irwin: bool = True
    has_irwvp: bool = True
    has_vschn: bool = False
    satellite_channels: List[str] = ["IRWIN", "IRWVP"]
    ri_risk_index: Optional[float] = None
    operating_threshold: float = 0.125
    ri_flag: Optional[bool] = None
    risk_category: Optional[str] = None
    source_status: str = "NOAA IBTrACS + HURSAT-B1 Verified"
    is_canonical: bool = False


class HistoricalOutcomeVerification(BaseModel):
    """
    Historical outcome for post-event verification.
    CRITICAL: MUST NEVER BE PROVIDED AS MODEL INPUT.
    """
    title: str = "HISTORICAL OUTCOME — NOT USED AS MODEL INPUT"
    observation_time: str
    verification_time_24h: str
    observed_future_wind_kts: float
    observed_delta_v_24h: float
    ri_occurred: bool
    wmo_ri_criterion: str = "Maximum sustained 1-minute wind speed increase >= 30 kts in 24 hours"
    disclaimer: str = (
        "Ground truth verified from NOAA IBTrACS historical reanalysis. "
        "This information represents future state (t + 24h) and was strictly hidden from model inference."
    )


class AttributionEntry(BaseModel):
    feature_name: str
    display_name: str
    direction: str  # "supports_ri" or "suppresses_ri"
    attribution_score: float
    contribution_magnitude: float
    normalized_value: Optional[float] = None
    explanation_note: str


class ModelFeatureAttributionSummary(BaseModel):
    title: str = "Model Feature Attribution"
    method: str = "Standardized Linear Coefficient Weighting"
    top_supporting_features: List[AttributionEntry] = []
    top_suppressing_features: List[AttributionEntry] = []
    attribution_disclaimer: str = (
        "Attributions describe statistical model behavior within the regularized linear decision space, "
        "not physical meteorological causality."
    )


class TemporalIndicatorsSummary(BaseModel):
    current_wind_kts: float
    wind_change_6h_kts: Optional[float] = None
    wind_change_12h_kts: Optional[float] = None
    central_pressure_mb: Optional[float] = None
    pressure_drop_6h_mb: Optional[float] = None
    translation_speed_kts: Optional[float] = None
    translation_bearing_deg: Optional[float] = None
    translation_heading: Optional[str] = None
    source_label: str = "Derived from observation history (NOAA IBTrACS best-track sequence)"


class SatelliteStructuralEvidenceSummary(BaseModel):
    source: str = "NOAA HURSAT-B1 Geostationary Infrared"
    channels_available: List[str] = []
    has_irwin: bool = True
    has_irwvp: bool = False
    has_vschn: bool = False
    irwin_mean_tb_k: Optional[float] = None
    irwin_min_tb_k: Optional[float] = None
    cold_cloud_fraction_233k: Optional[float] = None
    very_cold_cloud_fraction_219k: Optional[float] = None
    overshooting_top_fraction_203k: Optional[float] = None
    core_convection_mean_k: Optional[float] = None
    core_ring_temperature_diff_k: Optional[float] = None
    azimuthal_symmetry_metric: Optional[float] = None
    imagery_endpoint: Optional[str] = None


class ModelScoreSummary(BaseModel):
    model_name: str = "CycloneGuard-RI-Multimodal-TS-Final"
    model_version: str = "v3.0.0-frozen"
    ri_risk_index: float
    operating_threshold: float = 0.125
    ri_flag: bool
    risk_category: str
    forecast_horizon_hours: float = 24.0
    score_label: str = "Empirical RI Risk Index"
    threshold_label: str = "Operating Decision Threshold (τ = 0.125)"
    calibration_status: str = "Uncalibrated Empirical Index"


class WhatTheModelSaw(BaseModel):
    """Complete representation of all information available at or before observation time."""
    observation_time_utc: str
    storm_id: str
    storm_name: str
    latitude: float
    longitude: float
    temporal_indicators: TemporalIndicatorsSummary
    temporal_features: Dict[str, float]
    satellite_evidence: SatelliteStructuralEvidenceSummary
    spatial_features: Dict[str, float]
    model_score: ModelScoreSummary
    model_feature_attribution: ModelFeatureAttributionSummary


class CaseStudyResponse(BaseModel):
    """Root response for historical cyclone case study experience."""
    storm_id: str
    storm_name: str
    basin: str
    international_id: Optional[str] = None
    summary: str
    lifecycle_start_utc: str
    lifecycle_end_utc: str
    peak_intensity_kts: float
    min_central_pressure_mb: Optional[float] = None
    total_verified_observations: int
    ri_events_count: int
    canonical_observation_time_utc: str
    selected_observation_time_utc: str
    timeline: List[TimelineObservationItem]
    what_the_model_saw: WhatTheModelSaw
    historical_outcome: HistoricalOutcomeVerification
    scientific_limitations: List[str]
    authoritative_warning_advisory: str
