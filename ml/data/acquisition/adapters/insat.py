"""
ISRO INSAT Acquisition Adapter for CycloneGuard.
Implements discovery and reports authentication requirements for ISRO MOSDAC data downlinks.
"""

from typing import Any, Dict, List, Optional
import os

from ml.data.acquisition.adapters.base_acquisition import (
    BaseAcquisitionAdapter,
    DiscoveredRemoteAsset,
)
from ml.data.acquisition.config import AcquisitionConfig
from ml.data.acquisition.downloader import DownloadExecutionResult


class INSATAcquisitionAdapter(BaseAcquisitionAdapter):
    """Acquisition adapter for ISRO INSAT-3D / 3DR Imager."""

    def __init__(self, config: Optional[AcquisitionConfig] = None):
        super().__init__("isro_insat3d_mosdac", config)

    def discover_remote_assets(self, query: Optional[Dict[str, Any]] = None) -> List[DiscoveredRemoteAsset]:
        """Returns catalog specifications for INSAT Level-1B products."""
        return [
            DiscoveredRemoteAsset(
                asset_id="insat3d_l1b_tir1_catalog",
                source_id=self.source_id,
                remote_url="https://www.mosdac.gov.in/api/v1/insat3d/l1b",
                file_name="3DIMG_TIR1.h5",
                time_coverage="2013-present",
                metadata={
                    "sensor": "INSAT-3D Imager",
                    "channel": "TIR1 (10.8 µm)",
                    "auth_required": True,
                    "resolution": "4 km",
                },
            ),
            DiscoveredRemoteAsset(
                asset_id="insat3dr_l1b_tir1_catalog",
                source_id=self.source_id,
                remote_url="https://www.mosdac.gov.in/api/v1/insat3dr/l1b",
                file_name="3RIMG_TIR1.h5",
                time_coverage="2016-present",
                metadata={
                    "sensor": "INSAT-3DR Imager",
                    "channel": "TIR1 (10.8 µm)",
                    "auth_required": True,
                    "resolution": "4 km",
                },
            ),
        ]

    def acquire_asset(
        self, asset: DiscoveredRemoteAsset, target_dir: Optional[str] = None
    ) -> DownloadExecutionResult:
        """Reports true authentication status without attempting unauthorized access."""
        has_token = bool(os.getenv("MOSDAC_API_TOKEN"))
        if not has_token:
            return DownloadExecutionResult(
                success=False,
                error_message="ISRO MOSDAC requires registered user authentication (MOSDAC_API_TOKEN). Anonymous downloads not supported by ISRO security policy.",
            )
        return DownloadExecutionResult(
            success=False,
            error_message="MOSDAC automated session handshake not configured.",
        )
