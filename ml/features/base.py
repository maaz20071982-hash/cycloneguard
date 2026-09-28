"""
CycloneGuard Feature Definition & Base Classes.

Enforces strict scientific metadata on every extracted feature:
- Source identifier
- Physical variable name
- Verified physical unit
- Clear distinction between RAW and DERIVED features
- Required input dependencies
- Missing data representation
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List, Optional


class FeatureType(str, Enum):
    """Data type of the feature value."""
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    BOOLEAN = "boolean"
    QUALITY_FLAG = "quality_flag"


class FeatureCategory(str, Enum):
    """Scientific category of the feature."""
    TRACK = "track"
    SATELLITE_RAW = "satellite_raw"
    SATELLITE_DERIVED = "satellite_derived"
    MORPHOLOGY = "morphology"
    TEMPORAL = "temporal"
    CROSS_SOURCE = "cross_source"
    DATA_QUALITY = "data_quality"


@dataclass(frozen=True)
class FeatureDefinition:
    """
    Metadata specification for an engineered cyclone feature.

    Guarantees that no feature exists in the AI pipeline without an explicit
    provenance, physical unit, and scientific justification.
    """
    name: str
    category: FeatureCategory
    feature_type: FeatureType
    source: str
    variable: str
    unit: str
    description: str
    required_inputs: List[str] = field(default_factory=list)
    is_raw: bool = False
    valid_range_min: Optional[float] = None
    valid_range_max: Optional[float] = None
    default_missing_value: Any = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "category": self.category.value,
            "feature_type": self.feature_type.value,
            "source": self.source,
            "variable": self.variable,
            "unit": self.unit,
            "description": self.description,
            "required_inputs": self.required_inputs,
            "is_raw": self.is_raw,
            "valid_range_min": self.valid_range_min,
            "valid_range_max": self.valid_range_max,
            "default_missing_value": self.default_missing_value,
        }
