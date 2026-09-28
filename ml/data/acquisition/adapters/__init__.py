"""
Acquisition adapters package.
"""

from ml.data.acquisition.adapters.base_acquisition import (
    BaseAcquisitionAdapter,
    DiscoveredRemoteAsset,
)
from ml.data.acquisition.adapters.hursat import HURSATAcquisitionAdapter
from ml.data.acquisition.adapters.insat import INSATAcquisitionAdapter

__all__ = [
    "BaseAcquisitionAdapter",
    "DiscoveredRemoteAsset",
    "HURSATAcquisitionAdapter",
    "INSATAcquisitionAdapter",
]
