"""
Data transfer objects and result schemas for CycloneGuard data adapters.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ValidationSeverity(str, Enum):
    VALID = "VALID"
    WARNING = "WARNING"
    ERROR = "ERROR"


class ValidationCheck(BaseModel):
    check_name: str
    passed: bool
    severity: ValidationSeverity
    message: str
    details: Optional[Dict[str, Any]] = None


class ValidationReport(BaseModel):
    source_id: str
    file_path: str
    status: ValidationSeverity
    checks: List[ValidationCheck] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    summary: str = ""

    @property
    def is_valid(self) -> bool:
        return self.status != ValidationSeverity.ERROR


class DiscoveredResource(BaseModel):
    resource_id: str
    source_id: str
    name: str
    remote_url: Optional[str] = None
    time_coverage: Optional[str] = None
    spatial_coverage: Optional[str] = None
    file_size_bytes: Optional[int] = None
    format: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DownloadStatus(str, Enum):
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
    SKIPPED_EXISTING = "SKIPPED_EXISTING"


class DownloadResult(BaseModel):
    source_id: str
    resource_id: str
    status: DownloadStatus
    local_path: Optional[str] = None
    file_size_bytes: int = 0
    checksum_sha256: Optional[str] = None
    message: str = ""
    download_time_utc: datetime = Field(default_factory=datetime.utcnow)


class ParsedData(BaseModel):
    source_id: str
    file_path: str
    records_count: int
    raw_variables: List[str]
    raw_dimensions: Dict[str, int]
    raw_attributes: Dict[str, Any] = Field(default_factory=dict)
    data_payload: Any = None


class NormalizedData(BaseModel):
    source_id: str
    normalized_type: str
    records_count: int
    time_range_utc: Optional[tuple[str, str]] = None
    spatial_bounds: Optional[Dict[str, float]] = None
    data_payload: Any = None
    units: Dict[str, str] = Field(default_factory=dict)
    normalization_log: List[str] = Field(default_factory=list)
