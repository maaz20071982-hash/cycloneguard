"""
Dataset Manifest System for CycloneGuard.
Tracks provenance, cryptographic integrity (SHA-256), spatial/temporal coverage,
variable schemas, and verification statuses for scientific datasets.
"""

from datetime import datetime
import json
import os
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from ml.data.adapters.base import BaseDataSourceAdapter


class DatasetManifest(BaseModel):
    source_id: str
    dataset_name: str
    version: str
    download_time_utc: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    file_name: str
    file_path: str
    file_size_bytes: int
    checksum_sha256: str
    time_range: Optional[Dict[str, str]] = None
    spatial_range: Optional[Dict[str, float]] = None
    variables: List[str] = Field(default_factory=list)
    record_count: int = 0
    status: str = "VERIFIED"
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def save(self, manifest_path: Optional[str] = None) -> str:
        """Saves the manifest to a JSON file."""
        if not manifest_path:
            base_dir = os.path.dirname(self.file_path)
            manifest_dir = os.path.join(base_dir, "..", "manifests")
            os.makedirs(manifest_dir, exist_ok=True)
            manifest_name = f"{os.path.basename(self.file_name)}.manifest.json"
            manifest_path = os.path.join(manifest_dir, manifest_name)

        os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(self.model_dump(), f, indent=2)
        return manifest_path

    @classmethod
    def load(cls, manifest_path: str) -> "DatasetManifest":
        """Loads a manifest from a JSON file."""
        if not os.path.exists(manifest_path):
            raise FileNotFoundError(f"Manifest not found: {manifest_path}")
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)

    def verify_integrity(self) -> bool:
        """Verifies that the target file matches the recorded size and SHA-256 checksum."""
        if not os.path.exists(self.file_path):
            return False
        if os.path.getsize(self.file_path) != self.file_size_bytes:
            return False
        current_sha256 = BaseDataSourceAdapter.compute_sha256(self.file_path)
        return current_sha256 == self.checksum_sha256


def generate_manifest_for_file(
    source_id: str,
    dataset_name: str,
    version: str,
    file_path: str,
    variables: Optional[List[str]] = None,
    time_range: Optional[Dict[str, str]] = None,
    spatial_range: Optional[Dict[str, float]] = None,
    record_count: int = 0,
    metadata: Optional[Dict[str, Any]] = None,
) -> DatasetManifest:
    """Generates a DatasetManifest from a verified physical file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Target file does not exist: {file_path}")

    size_bytes = os.path.getsize(file_path)
    sha256 = BaseDataSourceAdapter.compute_sha256(file_path)
    file_name = os.path.basename(file_path)

    manifest = DatasetManifest(
        source_id=source_id,
        dataset_name=dataset_name,
        version=version,
        file_name=file_name,
        file_path=os.path.abspath(file_path),
        file_size_bytes=size_bytes,
        checksum_sha256=sha256,
        time_range=time_range,
        spatial_range=spatial_range,
        variables=variables or [],
        record_count=record_count,
        status="VERIFIED",
        metadata=metadata or {},
    )
    return manifest
