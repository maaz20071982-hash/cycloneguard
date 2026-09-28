from sqlalchemy import Column, String, Boolean, JSON, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid


class ModelVersion(Base, TimestampMixin):
    """Initial schema for future AI model version metadata (Phase 7)."""
    __tablename__ = "model_versions"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    name = Column(String(100), nullable=False)  # e.g., CycloneNet-RI, IntensityCNN
    version = Column(String(50), nullable=False)  # e.g., v1.0.0
    architecture = Column(String(100), nullable=False)  # e.g., ResNet3D-ViT
    weights_path = Column(Text, nullable=True)
    is_active = Column(Boolean, default=False, nullable=False)
    metrics_manifest = Column(JSON, nullable=True)

    predictions = relationship("Prediction", back_populates="model_version_rel")

    def __repr__(self) -> str:
        return f"<ModelVersion {self.name} {self.version} (Active: {self.is_active})>"
