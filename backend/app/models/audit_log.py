from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import generate_uuid


class AuditLog(Base):
    """Immutable audit trail for tracking system events and administrative mutations (Sprint 3)."""
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False, index=True)
    resource_id = Column(String(100), nullable=True, index=True)
    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    metadata_json = Column(JSON, nullable=True)

    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"<AuditLog {self.action} on {self.resource_type}:{self.resource_id} by {self.user_id}>"
