"""
CycloneGuard Strict Inference Feature Contract (Sprint 12).

Defines and enforces the exact 61-feature schema contract for:
CycloneGuard-RI-Multimodal-TS-Final (v3.0.0-frozen).

Enforces:
1. Exact 61 feature names and sequence matching models/ri/final/feature_schema.json.
2. Separation into 23 Temporal Kinematic Features and 38 HURSAT Spatial Structural Features.
3. Strict type validation (numeric float / int / None / NaN).
4. Explicit missingness tracking (availability indicators; NEVER zero-filling unobserved channels).
5. Immediate rejection of environmental variables (strictly forbidden in production).
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from ml.datasets.spatial_ri_dataset import (
    TEMPORAL_FEATURE_NAMES,
    SPATIAL_FEATURE_NAMES,
)

# Canonical 61 features in immutable sequence
CANONICAL_FEATURE_CONTRACT: Tuple[str, ...] = (*TEMPORAL_FEATURE_NAMES, *SPATIAL_FEATURE_NAMES)
CANONICAL_TEMPORAL_FEATURES: Tuple[str, ...] = TEMPORAL_FEATURE_NAMES
CANONICAL_SPATIAL_FEATURES: Tuple[str, ...] = SPATIAL_FEATURE_NAMES


class FeatureContractViolationError(ValueError):
    """Raised when an inference payload violates the 61-feature production schema contract."""
    def __init__(
        self,
        message: str,
        missing_features: Optional[List[str]] = None,
        invalid_types: Optional[Dict[str, str]] = None,
        forbidden_features: Optional[List[str]] = None,
    ):
        super().__init__(message)
        self.missing_features = missing_features or []
        self.invalid_types = invalid_types or {}
        self.forbidden_features = forbidden_features or []


# Backward compatibility aliases and specific subclasses
FeatureContractValidationError = FeatureContractViolationError


class EnvironmentalFeatureForbiddenError(FeatureContractViolationError):
    """Raised when forbidden environmental features (env_*) are submitted to the production pipeline."""
    pass


class InferenceFeatureContract:
    """
    Validates and standardizes input feature representations for frozen model inference.
    Supports both class-level methods and instance-level contract validation.
    """

    feature_names: List[str] = list(CANONICAL_FEATURE_CONTRACT)
    temporal_features: List[str] = list(CANONICAL_TEMPORAL_FEATURES)
    spatial_features: List[str] = list(CANONICAL_SPATIAL_FEATURES)

    def __init__(self):
        self.feature_names = list(CANONICAL_FEATURE_CONTRACT)
        self.temporal_features = list(CANONICAL_TEMPORAL_FEATURES)
        self.spatial_features = list(CANONICAL_SPATIAL_FEATURES)

    @classmethod
    def get_canonical_features(cls) -> Tuple[str, ...]:
        """Returns the immutable 61-feature tuple."""
        return CANONICAL_FEATURE_CONTRACT

    @classmethod
    def validate_feature_dict(cls, feature_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates an input dictionary against the strict 61-feature contract.
        
        Args:
            feature_dict: Dictionary containing candidate features.
            
        Returns:
            Validated, sanitized dictionary containing exactly the 61 canonical features.
            
        Raises:
            EnvironmentalFeatureForbiddenError: If environmental features are present.
            FeatureContractViolationError: If required keys are missing or types are invalid.
        """
        # 1. Check for forbidden environmental features
        forbidden = [k for k in feature_dict.keys() if k.startswith("env_")]
        if forbidden:
            raise EnvironmentalFeatureForbiddenError(
                f"Environmental features are strictly excluded from the frozen production model: {forbidden[:3]}",
                forbidden_features=forbidden,
            )

        # 2. Check for missing required feature keys
        missing = [f for f in CANONICAL_FEATURE_CONTRACT if f not in feature_dict]
        if missing:
            raise FeatureContractViolationError(
                f"Contract Violation: Missing {len(missing)} required features from 61-feature contract.",
                missing_features=missing,
            )

        # 3. Validate types and sanitize values
        sanitized: Dict[str, Any] = {}
        invalid_types: Dict[str, str] = {}

        for feat_name in CANONICAL_FEATURE_CONTRACT:
            val = feature_dict[feat_name]
            if val is None:
                sanitized[feat_name] = np.nan
            elif isinstance(val, (int, float, np.floating, np.integer)):
                if np.isnan(val):
                    sanitized[feat_name] = np.nan
                else:
                    sanitized[feat_name] = float(val)
            elif isinstance(val, bool):
                sanitized[feat_name] = 1.0 if val else 0.0
            else:
                try:
                    sanitized[feat_name] = float(val)
                except (ValueError, TypeError):
                    invalid_types[feat_name] = f"Cannot cast value '{val}' (type {type(val).__name__}) to float."

        if invalid_types:
            raise FeatureContractViolationError(
                f"Contract Violation: Found {len(invalid_types)} non-numeric feature values.",
                invalid_types=invalid_types,
            )

        return sanitized

    def validate_observation_features(self, feature_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Instance alias for validate_feature_dict."""
        return self.validate_feature_dict(feature_dict)

    def validate_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validates that a pandas DataFrame matches the 61-feature schema and ordering.
        """
        forbidden = [c for c in df.columns if str(c).startswith("env_")]
        if forbidden:
            raise EnvironmentalFeatureForbiddenError(
                f"Environmental features are strictly excluded from the frozen production model: {forbidden[:3]}",
                forbidden_features=forbidden,
            )

        missing = [f for f in CANONICAL_FEATURE_CONTRACT if f not in df.columns]
        if missing:
            raise FeatureContractViolationError(
                f"Contract Violation: Missing {len(missing)} required features from DataFrame: {missing[:5]}",
                missing_features=missing,
            )

        return df[list(CANONICAL_FEATURE_CONTRACT)].copy()

    def preprocess_features(
        self,
        features: Dict[str, Any],
        allow_missing_spatial: bool = True,
    ) -> Dict[str, float]:
        """
        Preprocesses a dictionary of features. If spatial features are not supplied,
        explicit missingness indicators are populated (has_irwvp=0.0, has_vschn=0.0)
        and unobserved fields set to np.nan so they are imputed via the train-fitted median imputer.
        """
        # Check forbidden first
        forbidden = [k for k in features.keys() if k.startswith("env_")]
        if forbidden:
            raise EnvironmentalFeatureForbiddenError(
                f"Environmental features are strictly excluded from the frozen production model: {forbidden[:3]}",
                forbidden_features=forbidden,
            )

        result: Dict[str, float] = {}

        # 1. Process temporal features
        for f in CANONICAL_TEMPORAL_FEATURES:
            val = features.get(f, np.nan)
            result[f] = float(val) if val is not None and not np.isnan(val) else np.nan

        # 2. Process spatial features
        has_spatial_in_input = any(f in features for f in CANONICAL_SPATIAL_FEATURES if not f.startswith("has_"))

        if not has_spatial_in_input and allow_missing_spatial:
            for f in CANONICAL_SPATIAL_FEATURES:
                if f in ("has_irwvp", "has_vschn"):
                    result[f] = 0.0
                else:
                    result[f] = np.nan
        else:
            for f in CANONICAL_SPATIAL_FEATURES:
                val = features.get(f, np.nan)
                result[f] = float(val) if val is not None and not np.isnan(val) else np.nan

        return self.validate_feature_dict(result)

    @classmethod
    def assemble_contract_vector(
        cls,
        temporal_dict: Dict[str, Any],
        spatial_dict: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Combines separate temporal kinematic and satellite spatial dictionaries into
        the unified 61-feature contract.
        Strictly enforces zero lookahead: rejects any future ground truth or target variables.
        """
        all_keys = list(temporal_dict.keys()) + list(spatial_dict.keys())
        forbidden_lookahead = [k for k in all_keys if "future" in k.lower() or "target" in k.lower() or "delta_v_24h" in k.lower()]
        if forbidden_lookahead:
            raise FeatureContractViolationError(
                f"Lookahead violation: Future ground truth variables are strictly forbidden from inference vectors: {forbidden_lookahead}",
                forbidden_features=forbidden_lookahead,
            )

        combined = {}
        for f in CANONICAL_TEMPORAL_FEATURES:
            combined[f] = temporal_dict.get(f, np.nan)
        for f in CANONICAL_SPATIAL_FEATURES:
            combined[f] = spatial_dict.get(f, np.nan)

        return cls.validate_feature_dict(combined)

