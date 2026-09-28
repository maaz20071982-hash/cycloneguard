"""
CycloneGuard Frozen Model Loader (Sprint 12 Production Inference Engine).

Strictly loads and executes the frozen scientific production artifact:
- Model Name: CycloneGuard-RI-Multimodal-TS-Final
- Version: v3.0.0-frozen
- Path: models/ri/final/
- Artifacts: model.pkl, scaler.pkl, imputer.pkl, feature_schema.json, model_manifest.json
- Contract: Exactly 61 features (23 temporal kinematics + 38 HURSAT-B1 spatial structural proxies).

NON-NEGOTIABLE INTEGRITY RULES:
1. Loads exclusively from models/ri/final/.
2. Fails loudly on schema mismatch, missing artifacts, or version discrepancies.
3. NEVER falls back to historical v1/v2 models.
4. Preserves explicit missingness tracking (never zero-fills missing features).
"""

import json
import os
import pickle
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import numpy as np


class FrozenModelLoadError(RuntimeError):
    """Raised when the frozen model artifacts cannot be found or validated."""
    pass


class FrozenModelSchemaMismatchError(ValueError):
    """Raised when the input feature vector or saved schema violates the 61-feature contract."""
    pass


class FrozenModelInferenceError(RuntimeError):
    """Raised when inference fails during array transformation or model evaluation."""
    pass


class FrozenModelLoader:
    """
    Production-grade loader and inference runner for CycloneGuard-RI-Multimodal-TS-Final (v3.0.0-frozen).
    """

    EXPECTED_MODEL_NAME = "CycloneGuard-RI-Multimodal-TS-Final"
    EXPECTED_VERSION = "v3.0.0-frozen"
    EXPECTED_FEATURE_COUNT = 61

    def __init__(self, artifact_dir: Optional[str] = None):
        """
        Initializes the frozen loader. Strictly validates all artifacts upon instantiation.
        """
        if artifact_dir is None:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            artifact_dir = os.path.join(project_root, "models", "ri", "final")

        self.artifact_dir = os.path.abspath(artifact_dir)
        self.model = None
        self.scaler = None
        self.imputer = None
        self.manifest = {}
        self.schema = {}
        self.feature_names: List[str] = []
        self._load_and_validate_artifacts()

    @property
    def is_loaded(self) -> bool:
        """Returns True if the frozen model artifact is loaded and verified."""
        return self.model is not None

    @property
    def model_version(self) -> str:
        """Returns the certified frozen model version."""
        return self.manifest.get("model_version", self.EXPECTED_VERSION)

    @property
    def feature_count(self) -> int:
        """Returns the canonical feature count (61)."""
        return len(self.feature_names)

    @property
    def project_root(self) -> str:
        """Returns the project root directory."""
        return os.path.abspath(os.path.join(self.artifact_dir, "..", "..", ".."))

    @property
    def model_dir(self) -> str:
        """Alias for artifact_dir."""
        return self.artifact_dir

    def _load_and_validate_artifacts(self) -> None:
        """Loads and strictly validates all required frozen artifacts."""
        if not os.path.isdir(self.artifact_dir):
            raise FrozenModelLoadError(
                f"Frozen model directory not found: '{self.artifact_dir}'. "
                "Refusing silent fallback to uncertified historical models."
            )

        manifest_path = os.path.join(self.artifact_dir, "model_manifest.json")
        schema_path = os.path.join(self.artifact_dir, "feature_schema.json")
        model_path = os.path.join(self.artifact_dir, "model.pkl")
        scaler_path = os.path.join(self.artifact_dir, "scaler.pkl")
        imputer_path = os.path.join(self.artifact_dir, "imputer.pkl")

        for path, name in [
            (manifest_path, "model_manifest.json"),
            (schema_path, "feature_schema.json"),
            (model_path, "model.pkl"),
            (scaler_path, "scaler.pkl"),
            (imputer_path, "imputer.pkl"),
        ]:
            if not os.path.isfile(path):
                raise FrozenModelLoadError(
                    f"Required frozen artifact '{name}' missing from '{self.artifact_dir}'. "
                    "Inference pipeline cannot initialize."
                )

        # 1. Validate manifest
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                self.manifest = json.load(f)
        except Exception as e:
            raise FrozenModelLoadError(f"Failed to parse model manifest: {e}") from e

        version = self.manifest.get("model_version")
        if version != self.EXPECTED_VERSION:
            raise FrozenModelLoadError(
                f"Model version mismatch in manifest: expected '{self.EXPECTED_VERSION}', "
                f"got '{version}'."
            )

        # 2. Validate feature schema
        try:
            with open(schema_path, "r", encoding="utf-8") as f:
                self.schema = json.load(f)
        except Exception as e:
            raise FrozenModelLoadError(f"Failed to parse feature schema: {e}") from e

        self.feature_names: List[str] = self.schema.get("feature_names", [])
        if len(self.feature_names) != self.EXPECTED_FEATURE_COUNT:
            raise FrozenModelSchemaMismatchError(
                f"Feature count mismatch in schema: expected {self.EXPECTED_FEATURE_COUNT}, "
                f"got {len(self.feature_names)}."
            )

        # 3. Load model, scaler, and imputer
        try:
            with open(model_path, "rb") as f:
                self.model = pickle.load(f)
            with open(scaler_path, "rb") as f:
                self.scaler = pickle.load(f)
            with open(imputer_path, "rb") as f:
                self.imputer = pickle.load(f)
        except Exception as e:
            raise FrozenModelLoadError(f"Failed to deserialized model binaries: {e}") from e

        # Operating threshold
        self.operating_threshold = float(self.manifest.get("operating_decision_threshold", 0.125))

    def get_manifest_metadata(self) -> Dict[str, Any]:
        """Returns the complete immutable model manifest."""
        return self.manifest.copy()

    def predict_from_feature_dict(
        self,
        features: Dict[str, Any],
        threshold_override: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Executes inference for a single observation using an input feature dictionary.
        
        Args:
            features: Dictionary containing feature key-value pairs.
            threshold_override: Optional custom decision threshold (strictly for sensitivity analysis).
            
        Returns:
            Dictionary containing the empirical risk index, classification flag,
            operating threshold, feature attributions, and provenance metadata.
        """
        # Validate that all 61 expected features are present in the dictionary
        missing_keys = [f for f in self.feature_names if f not in features]
        if missing_keys:
            raise FrozenModelSchemaMismatchError(
                f"Input observation violates 61-feature contract. Missing {len(missing_keys)} required features: "
                f"{missing_keys[:5]}..."
            )

        # Assemble strictly ordered array
        raw_vector = np.array(
            [[float(features[f]) if features[f] is not None and not (isinstance(features[f], float) and np.isnan(features[f])) else np.nan for f in self.feature_names]],
            dtype=float,
        )

        try:
            # Impute missing values using train-fitted medians
            imputed_vector = self.imputer.transform(raw_vector)
            # Scale using train-fitted standard scaler
            scaled_vector = self.scaler.transform(imputed_vector)
            # Predict probabilities
            probs = self.model.predict_proba(scaled_vector)[0]
        except Exception as e:
            raise FrozenModelInferenceError(f"Inference computation failed: {e}") from e

        risk_index = float(probs[1]) if len(probs) > 1 else float(probs[0])
        decision_th = float(threshold_override) if threshold_override is not None else self.operating_threshold
        ri_flag = bool(risk_index >= decision_th)

        # Assign risk category based on Phase 5 specification
        if risk_index < decision_th:
            risk_category = "LOW_RISK"
        elif risk_index < 0.350:
            risk_category = "ELEVATED_RISK"
        else:
            risk_category = "HIGH_RISK"

        # Compute standardized linear feature attributions
        coefs = self.model.coef_[0]
        scaled_vals = scaled_vector[0]
        contributions = coefs * scaled_vals

        top_supporting = []
        top_suppressing = []
        for i, fname in enumerate(self.feature_names):
            contrib = float(contributions[i])
            item = {
                "feature_name": fname,
                "raw_value": round(float(raw_vector[0, i]), 4) if not np.isnan(raw_vector[0, i]) else None,
                "standardized_value": round(float(scaled_vals[i]), 4),
                "model_coefficient": round(float(coefs[i]), 4),
                "attribution_score": round(contrib, 4),
                "direction": "supports_ri" if contrib > 0 else "suppresses_ri",
            }
            if contrib > 0:
                top_supporting.append(item)
            else:
                top_suppressing.append(item)

        top_supporting.sort(key=lambda x: x["attribution_score"], reverse=True)
        top_suppressing.sort(key=lambda x: x["attribution_score"])

        return {
            "model_name": self.EXPECTED_MODEL_NAME,
            "model_version": self.EXPECTED_VERSION,
            "ri_risk_index": round(risk_index, 4),
            "operating_threshold": round(decision_th, 3),
            "ri_flag": ri_flag,
            "risk_category": risk_category,
            "forecast_horizon_hours": 24.0,
            "calibration_status": "Uncalibrated Empirical Risk Index (Platt scaling unvalidated due to sample scale)",
            "top_supporting_features": top_supporting[:5],
            "top_suppressing_features": top_suppressing[:5],
            "inference_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }

    def predict_single(
        self,
        features: Dict[str, Any],
        threshold_override: Optional[float] = None,
    ) -> Tuple[float, Dict[str, Any]]:
        """Convenience method returning (ri_risk_index, attribution_dict)."""
        res = self.predict_from_feature_dict(features, threshold_override=threshold_override)
        return res["ri_risk_index"], {
            "top_supporting": res["top_supporting_features"],
            "top_suppressing": res["top_suppressing_features"],
        }
