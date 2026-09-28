"""
CycloneGuard Rapid Intensification Inference Engine (RI Predictor v1).

Provides the operational inference interface for evaluating RI risk from real-time
or historical CycloneState representations without data fabrication.
"""

from datetime import datetime, timezone
import json
import os
import pickle
from typing import Any, Dict, List, Optional, Union
import numpy as np

from ml.features.cyclone_state import CycloneState, CycloneStateBuilder
from ml.features.state_encoder import CycloneStateEncoder
from ml.features.scaler import CycloneFeatureScaler
from ml.data.schemas.track import CycloneTrackPoint


class RIPredictor:
    """
    Production-grade inference engine for CycloneGuard Rapid Intensification Model v1.
    """

    def __init__(
        self,
        artifact_dir: str,
        override_threshold: Optional[float] = None,
    ):
        """
        Load versioned model artifact, scaler, and feature schema.
        """
        self.artifact_dir = artifact_dir

        model_path = os.path.join(artifact_dir, "model.pkl")
        scaler_path = os.path.join(artifact_dir, "scaler.json")
        schema_path = os.path.join(artifact_dir, "feature_schema.json")
        meta_path = os.path.join(artifact_dir, "metadata.json")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model binary not found at {model_path}")
        if not os.path.exists(scaler_path):
            raise FileNotFoundError(f"Scaler parameters not found at {scaler_path}")
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Feature schema not found at {schema_path}")

        with open(model_path, "rb") as f:
            self.model = pickle.load(f)

        self.scaler = CycloneFeatureScaler.load_json(scaler_path)

        with open(schema_path, "r", encoding="utf-8") as f:
            self.schema = json.load(f)

        self.metadata = {}
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)

        # Calibrator if present
        calib_path = os.path.join(artifact_dir, "calibrator.pkl")
        self.calibrator = None
        if os.path.exists(calib_path):
            with open(calib_path, "rb") as f:
                self.calibrator = pickle.load(f)

        self.encoder = CycloneStateEncoder()
        self.selected_indices: List[int] = self.schema.get("selected_indices", [])
        self.selected_feature_names: List[str] = self.schema.get("selected_feature_names", [])

        # Operational decision threshold
        if override_threshold is not None:
            self.decision_threshold = float(override_threshold)
        else:
            self.decision_threshold = float(self.metadata.get("decision_threshold", 0.05))

    @classmethod
    def load_default(cls, override_threshold: Optional[float] = None) -> "RIPredictor":
        """Load default v1 production artifact from models/ri/v1."""
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        default_dir = os.path.join(project_root, "models", "ri", "v1")
        if not os.path.exists(default_dir):
            # Fallback to baseline v1 if ri/v1 not created
            default_dir = os.path.join(project_root, "models", "baseline", "v1")
        return cls(artifact_dir=default_dir, override_threshold=override_threshold)

    def predict_state(
        self,
        cyclone_state: CycloneState,
        use_calibrated: bool = False,
    ) -> Dict[str, Any]:
        """
        Evaluate Rapid Intensification risk for a single CycloneState object.
        """
        # 1. Full 69-dim vector encoding
        full_vector = self.encoder.encode(cyclone_state).reshape(1, -1)

        # 2. Extract selected sub-features
        if self.selected_indices:
            sub_vector = full_vector[:, self.selected_indices]
        else:
            sub_vector = full_vector

        # 3. Transform with training-only fitted scaler
        sub_scaled = self.scaler.transform(sub_vector)

        # 4. Predict probability
        if use_calibrated and self.calibrator is not None:
            probs = self.calibrator.predict_proba(sub_scaled)[0]
            calib_label = "Calibrated (Platt Scaling)"
        else:
            probs = self.model.predict_proba(sub_scaled)[0]
            calib_label = "Uncalibrated Model Score"

        prob_ri = float(probs[1]) if len(probs) > 1 else float(probs[0])
        ri_flag = bool(prob_ri >= self.decision_threshold)
        risk_tier = "ELEVATED_RISK" if ri_flag else "LOW_RISK"

        # 5. Linear Feature Attribution
        attribution_list: List[Dict[str, Any]] = []
        if hasattr(self.model, "coef_"):
            coefs = self.model.coef_[0]
            contributions = []
            for idx, fname in enumerate(self.selected_feature_names):
                if idx < len(coefs):
                    score = float(coefs[idx] * sub_scaled[0, idx])
                    contributions.append((fname, score))

            # Sort descending by contribution
            contributions.sort(key=lambda x: abs(x[1]), reverse=True)
            for fname, score in contributions[:5]:
                attribution_list.append({
                    "feature_name": fname,
                    "attribution_score": round(score, 4),
                    "direction": "supports_ri" if score > 0 else "suppresses_ri",
                })

        # 6. Observational Quality & Downgrade Evaluation
        quality_data = cyclone_state.data_quality
        overall_quality = quality_data.get("quality_overall_flag", "UNKNOWN")
        limitations: List[str] = []

        if not quality_data.get("quality_ir_available", False):
            limitations.append(
                "Coincident infrared satellite imagery is absent; prediction is operating exclusively on track kinematics."
            )
        if not quality_data.get("quality_microwave_available", False):
            limitations.append(
                "Passive microwave radiometer data unavailable; internal core eyewall structure not directly observed."
            )
        limitations.append(
            "Model scores reflect empirical statistical correlation on North Indian Ocean historical cases; they do not establish physical causation."
        )

        return {
            "storm_id": cyclone_state.storm_id,
            "storm_name": cyclone_state.storm_name or "UNNAMED",
            "observation_time_utc": cyclone_state.timestamp_utc,
            "forecast_horizon_hours": 24.0,
            "ri_probability": round(prob_ri, 4),
            "score_interpretation": calib_label,
            "decision_threshold": self.decision_threshold,
            "ri_flag": ri_flag,
            "risk_tier": risk_tier,
            "scientific_definition": "WMO / NHC standard: Delta V >= 30 kts in 24 hours (Kaplan & DeMaria 2003)",
            "model_version": self.metadata.get("version", "v1.0.0"),
            "model_name": self.metadata.get("model_name", "CycloneGuard-RI-v1"),
            "data_quality": overall_quality,
            "available_sources": cyclone_state.available_sources,
            "missing_sources": cyclone_state.missing_sources,
            "contributing_features": attribution_list,
            "limitations": limitations,
            "prediction_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }

    def predict_track_point(
        self,
        current_track: CycloneTrackPoint,
        previous_track: Optional[CycloneTrackPoint] = None,
        hist_6h_track: Optional[CycloneTrackPoint] = None,
        hist_12h_track: Optional[CycloneTrackPoint] = None,
    ) -> Dict[str, Any]:
        """
        Convenience wrapper building CycloneState from track points and generating prediction.
        """
        state = CycloneStateBuilder.build_state(
            current_track=current_track,
            previous_track=previous_track,
            hist_6h_track=hist_6h_track,
            hist_12h_track=hist_12h_track,
        )
        return self.predict_state(state)
