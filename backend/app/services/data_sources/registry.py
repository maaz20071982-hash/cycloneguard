import os
import sys

_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from ml.data.registry import (
    DataSourceDefinition,
    DataSourceStatus,
    DataSourceType,
    DataSourceRegistry,
    DATA_SOURCE_CATALOG,
    registry,
)

__all__ = [
    "DataSourceDefinition",
    "DataSourceStatus",
    "DataSourceType",
    "DataSourceRegistry",
    "DATA_SOURCE_CATALOG",
    "registry",
]
