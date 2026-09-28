from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid


class Alert(Base, TimestampMixin):
    """Initial schema for future cyclone alerts and warnings (Phase 7)."""
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    cyclone_id = Column(String(36), ForeignKey("cyclones.id", ondelete="CASCADE"), nullable=False, index=True)
    severity = Column(String(30), nullable=False)  # ADVISORY, WATCH, WARNING, CRITICAL
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    target_region = Column(String(100), nullable=False)
    issued_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    cyclone = relationship("Cyclone", back_populates="alerts")

    def __repr__(self) -> str:
        return f"<Alert {self.severity}: {self.title}>"
