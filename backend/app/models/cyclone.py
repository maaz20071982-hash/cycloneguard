from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid


class Cyclone(Base, TimestampMixin):
    """Initial schema for future cyclone records (Phase 7)."""
    __tablename__ = "cyclones"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    name = Column(String(100), nullable=False, index=True)
    basin = Column(String(50), nullable=False, index=True)  # e.g., North Indian Ocean, W-Pacific
    international_id = Column(String(50), nullable=True, unique=True)
    status = Column(String(50), default="AWAITING_INGESTION", nullable=False)
    genesis_time = Column(DateTime(timezone=True), nullable=True)
    dissipation_time = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships defined for future extensions
    observations = relationship("Observation", back_populates="cyclone", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="cyclone", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="cyclone", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Cyclone {self.name} ({self.basin})>"
