"""
Base Acquisition Adapter Interface for CycloneGuard.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from ml.data.acquisition.config import AcquisitionConfig, default_config
from ml.data.acquisition.downloader import DownloadExecutionResult, ResilientDownloader


class DiscoveredRemoteAsset(BaseModel):
    asset_id: str
    source_id: str
    remote_url: str
    file_name: str
    file_size_estimate_bytes: Optional[int] = None
    storm_id: Optional[str] = None
    storm_name: Optional[str] = None
    year: Optional[int] = None
    time_coverage: Optional[str] = None
    metadata: Dict[str, Any] = {}


class BaseAcquisitionAdapter(ABC):
    """Abstract base class for all source acquisition adapters."""

    def __init__(self, source_id: str, config: Optional[AcquisitionConfig] = None):
        self.source_id = source_id
        self.config = config or default_config
        self.downloader = ResilientDownloader(self.config)

    @abstractmethod
    def discover_remote_assets(self, query: Optional[Dict[str, Any]] = None) -> List[DiscoveredRemoteAsset]:
        """Queries remote catalog or directory index to discover downloadable assets."""
        pass

    @abstractmethod
    def acquire_asset(self, asset: DiscoveredRemoteAsset, target_dir: Optional[str] = None) -> DownloadExecutionResult:
        """Executes bounded, verified download of the asset."""
        pass
