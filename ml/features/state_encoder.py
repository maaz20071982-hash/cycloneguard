"""
CycloneGuard Cyclone State Vector Encoder (state_schema_v1).

Transforms a structured CycloneState object into a fixed-length numerical feature vector
suitable for machine learning models.

Enforces:
1. Strict, immutable feature ordering
2. Explicit missing-data indicators (value + is_observed flag)
3. Deterministic, versioned encoding (state_schema_v1)
4. Zero silent zero-filling
"""

from typing import Any, Dict, List, Tuple
import numpy as np

from ml.features.cyclone_state import CycloneState

# Canonical list of numerical features extracted from the state
BASE_NUMERICAL_FEATURES: Tuple[str, ...] = (
    # Track kinematics
    "track_latitude",
    "track_longitude",
    "track_wind_speed",
    "track_pressure",
    "track_translation_speed_kts",
    "track_translation_bearing_deg",
    # Satellite radiometrics & distributions
    "sat_ir_min_temp",
    "sat_ir_mean_temp",
    "sat_ir_std_temp",
    "sat_ir_p10_temp",
    "sat_ir_p50_temp",
    "sat_ir_core_temp",
    "sat_ir_ring_temp",
    "sat_ir_eye_surround_diff",
    "sat_cold_cloud_fraction_200k",
    "sat_cold_cloud_fraction_210k",
    "sat_cold_cloud_fraction_220k",
    # Morphology
    "morph_radial_symmetry",
    "morph_convective_organization",
    "morph_eye_detected",
    "morph_eye_temperature_contrast",
    # Temporal dynamics
    "temp_delta_wind_6h",
    "temp_delta_wind_12h",
    "temp_delta_pressure_6h",
    "temp_wind_change_rate_per_hour",
    "temp_delta_ir_min_6h",
    # Cross-source metrics
    "cross_adt_track_diff_kts",
    "cross_convection_wind_plausibility",
    # Quality metrics
    "quality_temporal_gap_minutes",
    "quality_missing_pixels_fraction",
)

# Categorical mappings
CROSS_AGREEMENT_MAP: Dict[str, float] = {
    "insufficient_evidence": 0.0,
    "consistent": 1.0,
    "partially_consistent": 2.0,
    "disagreeing": 3.0,
}

QUALITY_FLAG_MAP: Dict[str, float] = {
    "INVALID": 0.0,
    "DEGRADED": 1.0,
    "PARTIAL_TRACK_ONLY": 1.5,
    "ACCEPTABLE": 2.0,
    "GOOD": 3.0,
}

# Sensor availability binary indicators
SENSOR_AVAILABILITY_FLAGS: Tuple[str, ...] = (
    "quality_track_available",
    "quality_ir_available",
    "quality_adt_available",
    "quality_insat_available",
    "quality_scatterometer_available",
    "quality_microwave_available",
    "quality_is_boundary_padded",
)


class CycloneStateEncoder:
    """
    Encodes CycloneState instances into fixed-length 1D numerical vectors.
    
    For each base numerical feature X, the encoder produces:
    - X_val: The numerical value (or 0.0 placeholder if unobserved)
    - X_is_observed: 1.0 if physically observed, 0.0 if missing/unobserved
    
    This guarantees that models can distinguish 'zero' from 'unobserved'.
    """
    SCHEMA_VERSION = "state_schema_v1"

    def __init__(self, default_impute_values: Dict[str, float] = None):
        """
        Args:
            default_impute_values: Optional training-derived imputation medians.
        """
        self.default_impute = default_impute_values or {}
        self._feature_names = self._build_feature_names()

    @property
    def feature_names(self) -> List[str]:
        """Return the complete ordered list of feature vector names."""
        return list(self._feature_names)

    @property
    def vector_dimension(self) -> int:
        """Total dimension of encoded feature vector."""
        return len(self._feature_names)

    def _build_feature_names(self) -> List[str]:
        names: List[str] = []
        # 1. Base numerical features + missingness indicators
        for feat in BASE_NUMERICAL_FEATURES:
            names.append(f"{feat}_val")
            names.append(f"{feat}_is_observed")

        # 2. Categorical features
        names.append("cross_intensity_agreement_code")
        names.append("quality_overall_flag_code")

        # 3. Sensor availability flags
        for flag in SENSOR_AVAILABILITY_FLAGS:
            names.append(flag)

        return names

    def encode(self, state: CycloneState) -> np.ndarray:
        """
        Encode a single CycloneState object into a 1D numpy vector.
        """
        flat = state.get_all_features_flat()
        vector_values: List[float] = []

        # 1. Base numerical features with missingness flags
        for feat in BASE_NUMERICAL_FEATURES:
            raw_val = flat.get(feat)
            if raw_val is not None and not (isinstance(raw_val, float) and np.isnan(raw_val)):
                val_float = float(raw_val)
                is_obs = 1.0
            else:
                val_float = self.default_impute.get(feat, 0.0)
                is_obs = 0.0

            vector_values.append(val_float)
            vector_values.append(is_obs)

        # 2. Categorical features
        cross_agree_str = flat.get("cross_intensity_agreement", "insufficient_evidence")
        vector_values.append(CROSS_AGREEMENT_MAP.get(str(cross_agree_str), 0.0))

        qual_flag_str = flat.get("quality_overall_flag", "DEGRADED")
        vector_values.append(QUALITY_FLAG_MAP.get(str(qual_flag_str), 1.0))

        # 3. Sensor availability flags
        for flag in SENSOR_AVAILABILITY_FLAGS:
            flag_val = 1.0 if flat.get(flag, False) else 0.0
            vector_values.append(flag_val)

        arr = np.array(vector_values, dtype=np.float64)
        return arr

    def to_schema_metadata(self) -> dict:
        """Return metadata describing this encoder schema."""
        return {
            "schema_version": self.SCHEMA_VERSION,
            "vector_dimension": self.vector_dimension,
            "feature_names": self.feature_names,
            "base_features_count": len(BASE_NUMERICAL_FEATURES),
            "sensor_flags_count": len(SENSOR_AVAILABILITY_FLAGS),
        }
