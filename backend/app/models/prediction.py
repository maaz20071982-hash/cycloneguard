"""
Prediction ORM Model (Sprint 12 Production Prediction Persistence).
"""

from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid


class Prediction(Base, TimestampMixin):
    """Stores AI Rapid Intensification and meteorological prediction records."""
    __tablename__ = "predictions"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    cyclone_id = Column(String(36), ForeignKey("cyclones.id", ondelete="CASCADE"), nullable=True, index=True)
    model_version_id = Column(String(36), ForeignKey("model_versions.id"), nullable=True)
    
    # Cyclone fix identifiers
    storm_id = Column(String(50), nullable=True, index=True)
    storm_name = Column(String(100), nullable=True, index=True)
    observation_time = Column(DateTime(timezone=True), nullable=True, index=True)
    prediction_time = Column(DateTime(timezone=True), nullable=True, index=True)

    # Model identification
    model_name = Column(String(100), default="CycloneGuard-RI-Multimodal-TS-Final", nullable=False)
    model_version = Column(String(50), default="v3.0.0-frozen", nullable=False, index=True)
    
    # Scientific prediction results
    ri_risk_index = Column(Float, nullable=False)
    operating_threshold = Column(Float, default=0.125, nullable=False)
    ri_flag = Column(Boolean, default=False, nullable=False)
    risk_category = Column(String(30), default="LOW_RISK", nullable=False, index=True)
    forecast_horizon_hours = Column(Float, default=24.0, nullable=False)

    # Evidence stream flags
    temporal_evidence_available = Column(Boolean, default=True, nullable=False)
    satellite_evidence_available = Column(Boolean, default=True, nullable=False)
    satellite_channels = Column(JSON, nullable=True)

    # Traceability & Provenance
    input_provenance = Column(JSON, nullable=True)
    explanation_metadata = Column(JSON, nullable=True)
    requested_by = Column(String(100), nullable=True)

    # Legacy fields for backwards compatibility
    estimated_vmax_knots = Column(Float, nullable=True)
    estimated_mslp_hpa = Column(Float, nullable=True)
    ri_probability_24h = Column(Float, nullable=True)  # Legacy alias
    ri_risk_level = Column(String(30), nullable=True)   # Legacy alias

    # Relationships
    cyclone = relationship("Cyclone", back_populates="predictions")
    model_version_rel = relationship("ModelVersion", back_populates="predictions")

    def __repr__(self) -> str:
        return f"<Prediction {self.id} for Storm {self.storm_name or self.storm_id}: {self.risk_category} ({self.ri_risk_index:.3f})>"
