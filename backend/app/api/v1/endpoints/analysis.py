"""
CycloneGuard AI Analysis Service Endpoints.

Provides the API interface for future AI inference and cyclone state evaluation:
- State extraction and representation
- Baseline Rapid Intensification risk score
- Feature attribution and explanation
- Strict scientific honesty: Forecast models report 'uninitialized' without simulated paths
"""

import json
import os
import pickle
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.responses import success_response
from app.api.v1.deps import get_current_user
from app.models.user import User
from ml.data.schemas.track import CycloneTrackPoint
from ml.features.cyclone_state import CycloneStateBuilder
from ml.features.state_encoder import CycloneStateEncoder
from ml.features.scaler import CycloneFeatureScaler

router = APIRouter(prefix="/analysis", tags=["AI Analysis & Inference"])


class CycloneAnalysisRequest(BaseModel):
    """Payload for cyclone analysis request."""
    storm_id: str = Field(..., description="Unique storm identifier (e.g. '2023129N08091')")
    storm_name: Optional[str] = Field(None, description="Designated storm name (e.g. 'MOCHA')")
    timestamp_utc: Optional[str] = Field(None, description="Observation timestamp in UTC ISO-8601")
    latitude: float = Field(..., description="Center latitude in degrees north")
    longitude: float = Field(..., description="Center longitude in degrees east")
    wind_speed_kts: Optional[float] = Field(None, description="Current sustained wind speed in knots")
    central_pressure_mb: Optional[float] = Field(None, description="Current minimum central pressure in mb")


@router.post("/cyclone", summary="Analyze cyclone state and evaluate RI baseline risk")
def analyze_cyclone_state(
    payload: CycloneAnalysisRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Transforms observational inputs into a standardized CycloneState and evaluates
    Rapid Intensification probability using the verified Sprint 5 baseline model.
    """
    obs_time = payload.timestamp_utc or datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    # 1. Build standardized CycloneTrackPoint
    pt = CycloneTrackPoint(
        storm_id=payload.storm_id,
        storm_name=payload.storm_name or "UNNAMED",
        season=datetime.utcnow().year,
        basin="NI",
        timestamp_utc=obs_time,
        latitude=payload.latitude,
        longitude=payload.longitude,
        wind_speed_kts=payload.wind_speed_kts,
        central_pressure_mb=payload.central_pressure_mb,
    )

    # 2. Build CycloneState
    state = CycloneStateBuilder.build_state(current_track=pt)

    # 3. Check for baseline model artifact
    baseline_dir = os.path.join(settings.PROJECT_ROOT, "models", "baseline", "v1")
    model_path = os.path.join(baseline_dir, "model.pkl")
    scaler_path = os.path.join(baseline_dir, "scaler.json")
    schema_path = os.path.join(baseline_dir, "feature_schema.json")
    meta_path = os.path.join(baseline_dir, "metadata.json")

    ri_assessment = None
    explanation = None

    if (
        os.path.exists(model_path)
        and os.path.exists(scaler_path)
        and os.path.exists(schema_path)
    ):
        try:
            with open(model_path, "rb") as f:
                model = pickle.load(f)
            scaler = CycloneFeatureScaler.load_json(scaler_path)
            with open(schema_path, "r", encoding="utf-8") as f:
                schema_data = json.load(f)

            # Encode state vector
            encoder = CycloneStateEncoder()
            full_vector = encoder.encode(state).reshape(1, -1)
            selected_idx = schema_data.get("selected_indices", list(range(full_vector.shape[1])))
            sub_vector = full_vector[:, selected_idx]

            # Scale and predict
            sub_scaled = scaler.transform(sub_vector)
            prob_ri = float(model.predict_proba(sub_scaled)[0, 1])

            # Operational threshold: 0.05 from training optimization on imbalanced dataset
            best_th = 0.05
            is_ri_risk = prob_ri >= best_th

            ri_assessment = {
                "model_version": "v1.0.0-baseline",
                "ri_probability": round(prob_ri, 4),
                "decision_threshold": best_th,
                "risk_tier": "ELEVATED_RISK" if is_ri_risk else "LOW_RISK",
                "target_horizon_hours": 24.0,
                "scientific_standard": "WMO / NHC (Delta V >= 30 kts in 24h)",
            }

            # Top feature attributions (coefficients * normalized value)
            if hasattr(model, "coef_"):
                coefs = model.coef_[0]
                feature_names = schema_data.get("feature_names", [])
                contributions = {}
                for idx, fname in enumerate(feature_names):
                    if idx < len(coefs):
                        contributions[fname] = float(coefs[idx] * sub_scaled[0, idx])

                top_positive = sorted(contributions.items(), key=lambda x: x[1], reverse=True)[:3]
                top_negative = sorted(contributions.items(), key=lambda x: x[1])[:3]

                explanation = {
                    "method": "linear_feature_attribution",
                    "top_supporting_features": [
                        {"feature": k, "attribution": round(v, 4)} for k, v in top_positive if v > 0
                    ],
                    "top_suppressing_features": [
                        {"feature": k, "attribution": round(v, 4)} for k, v in top_negative if v < 0
                    ],
                    "disclaimer": (
                        "Attribution scores reflect statistical model weights within the linear baseline. "
                        "They do not establish physical causation."
                    ),
                }

        except Exception as e:
            ri_assessment = {
                "status": "Inference error",
                "error": str(e),
            }

    return success_response(data={
        "storm_id": payload.storm_id,
        "storm_name": payload.storm_name,
        "timestamp_utc": obs_time,
        "cyclone_state": state.model_dump(),
        "current_intensity": {
            "wind_speed_kts": payload.wind_speed_kts,
            "central_pressure_mb": payload.central_pressure_mb,
            "source": "noaa_ibtracs",
        },
        "ri_baseline_assessment": ri_assessment,
        "forecast": {
            "status": "Uninitialized",
            "message": "Neural trajectory forecasting model is scheduled for future development sprints.",
        },
        "explanation": explanation,
    })
