"""
Base Data Source Adapter Interface for CycloneGuard.
Enforces consistent data ingestion, validation, parsing, and normalization contracts.
"""

from abc import ABC, abstractmethod
import hashlib
import os
from typing import Any, Dict, List, Optional

from ml.data.registry import DataSourceDefinition, registry
from ml.data.schemas.adapter_results import (
    DiscoveredResource,
    DownloadResult,
    DownloadStatus,
    NormalizedData,
    ParsedData,
    ValidationReport,
    ValidationSeverity,
)


class BaseDataSourceAdapter(ABC):
    """Abstract Base Class for all CycloneGuard data source adapters."""

    def __init__(self, source_id: str):
        self.source_id = source_id
        self._definition: Optional[DataSourceDefinition] = registry.get_source(source_id)

    @property
    def definition(self) -> Optional[DataSourceDefinition]:
        return self._definition

    @abstractmethod
    def discover(self, filters: Optional[Dict[str, Any]] = None) -> List[DiscoveredResource]:
        """Discovers available remote resources, files, or streams matching criteria."""
        pass

    @abstractmethod
    def download(self, resource_id: str, target_dir: str) -> DownloadResult:
        """
        Downloads a specific discovered resource to local storage.
        If automated downloading is not implemented, returns DownloadResult with status NOT_IMPLEMENTED.
        """
        pass

    @abstractmethod
    def validate(self, file_path: str) -> ValidationReport:
        """Validates file integrity, readable structure, dimensions, and coordinate bounds."""
        pass

    @abstractmethod
    def parse(self, file_path: str) -> ParsedData:
        """Parses the raw file into raw data payloads, dimensions, and variable maps."""
        pass

    @abstractmethod
    def normalize(self, parsed_data: ParsedData) -> NormalizedData:
        """Normalizes parsed raw data to standard CycloneGuard scientific conventions (UTC, SI/knots/Kelvin)."""
        pass

    @staticmethod
    def compute_sha256(file_path: str) -> str:
        """Computes the SHA-256 checksum of a local file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
