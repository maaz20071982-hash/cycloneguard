"""
Satellite Asset Manifest System for CycloneGuard.
Tracks provenance, cryptographic checksums, spatial bounds, dimensions,
and validity statuses in a scalable JSON Lines (.jsonl) format.
"""

from datetime import datetime
import json
import os
from typing import Any, Dict, Iterator, List, Optional
from pydantic import BaseModel, Field

from ml.data.adapters.base import BaseDataSourceAdapter


class SatelliteAssetManifestRecord(BaseModel):
    """Machine-readable manifest entry for an individual satellite observation asset."""
    asset_id: str
    source: str
    product: str
    sensor: str
    channel: str
    channels: List[str] = Field(default_factory=list)
    timestamp: str  # ISO 8601 UTC
    storm_id: Optional[str] = None
    storm_name: Optional[str] = None
    file_path: str
    file_size: int
    checksum: str  # SHA-256
    coverage: Dict[str, float]  # lat_min, lat_max, lon_min, lon_max
    spatial_resolution_deg: Optional[float] = None
    dimensions: List[int] = Field(default_factory=list)
    processing_level: str = "L2"
    status: str = "VALID"  # VALID, DEGRADED, REJECTED
    quality_flags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SatelliteManifestStore:
    """Read/Write manager for the central satellite manifest JSONL file."""

    def __init__(self, manifest_file: Optional[str] = None):
        if manifest_file is None:
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
            manifest_file = os.path.join(root_dir, "data", "manifests", "satellite_manifest.jsonl")
        self.manifest_file = manifest_file

    def write_records(self, records: List[SatelliteAssetManifestRecord], append: bool = False):
        """Writes manifest records to the JSONL file."""
        os.makedirs(os.path.dirname(os.path.abspath(self.manifest_file)), exist_ok=True)
        mode = "a" if append else "w"
        with open(self.manifest_file, mode, encoding="utf-8") as f:
            for rec in records:
                line = json.dumps(rec.model_dump(), sort_keys=True)
                f.write(line + "\n")

    def read_records(self) -> List[SatelliteAssetManifestRecord]:
        """Reads all records from the manifest JSONL file."""
        if not os.path.exists(self.manifest_file):
            return []
        records = []
        with open(self.manifest_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    records.append(SatelliteAssetManifestRecord(**data))
        return records

    def find_by_storm(self, storm_id: str) -> List[SatelliteAssetManifestRecord]:
        return [r for r in self.read_records() if r.storm_id == storm_id]

    def find_by_time_window(
        self, start_iso: str, end_iso: str
    ) -> List[SatelliteAssetManifestRecord]:
        records = self.read_records()
        return [r for r in records if start_iso <= r.timestamp <= end_iso]

    def verify_all_checksums(self) -> Dict[str, bool]:
        """Verifies physical file existence and SHA-256 match for every recorded asset."""
        results = {}
        for rec in self.read_records():
            if not os.path.exists(rec.file_path):
                results[rec.asset_id] = False
                continue
            curr_sha = BaseDataSourceAdapter.compute_sha256(rec.file_path)
            results[rec.asset_id] = (curr_sha.lower() == rec.checksum.lower())
        return results
