from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid


class Observation(Base, TimestampMixin):
    """Initial schema for future multi-source satellite observations (Phase 7)."""
    __tablename__ = "observations"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    cyclone_id = Column(String(36), ForeignKey("cyclones.id", ondelete="CASCADE"), nullable=False, index=True)
    source = Column(String(50), nullable=False)  # INSAT-3D, HIMAWARI-9, GOES-16, ERA5
    channel = Column(String(50), nullable=False)  # IR1, WV, VIS, Passive Microwave
    observation_time = Column(DateTime(timezone=True), nullable=False, index=True)
    storage_path = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True)

    cyclone = relationship("Cyclone", back_populates="observations")

    def __repr__(self) -> str:
        return f"<Observation {self.source} - {self.channel} @ {self.observation_time}>"
