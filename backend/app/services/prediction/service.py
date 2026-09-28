"""
CycloneGuard Prediction Service (Sprint 12 Production Prediction Service Layer).

Encapsulates all inference logic, feature contract validation, model execution,
risk index presentation mapping, provenance assembly, and persistence.
Strictly isolates the API layer from direct manipulation of scikit-learn models.
"""

from datetime import datetime, timezone
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from sqlalchemy.orm import Session

from app.core.config import settings
if settings.PROJECT_ROOT not in sys.path:
    sys.path.insert(0, settings.PROJECT_ROOT)
from app.core.exceptions import (
    FeatureContractInvalidError,
    ModelUnavailableError,
    NotFoundError,
    ObservationNotFoundError,
    PredictionFailedError,
)
from app.models.prediction import Prediction
from app.schemas.prediction import (
    DataProvenance,
    FeatureAttributionItem,
    PredictionRequest,
    PredictionResponse,
)
from app.services.audit_service import AuditService
from ml.inference.feature_contract import (
    CANONICAL_FEATURE_CONTRACT,
    FeatureContractViolationError,
    InferenceFeatureContract,
)
from ml.inference.frozen_model import (
    FrozenModelInferenceError,
    FrozenModelLoadError,
    FrozenModelLoader,
    FrozenModelSchemaMismatchError,
)

logger = logging.getLogger("cycloneguard.prediction_service")


class PredictionService:
    """
    Production-grade service executing inferences with CycloneGuard-RI-Multimodal-TS-Final (v3.0.0-frozen).
    """

    _cached_loader: Optional[FrozenModelLoader] = None
    _cached_historical_samples: Optional[List[Any]] = None

    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self.model_loader = self._get_loader()

    @classmethod
    def _get_loader(cls) -> FrozenModelLoader:
        """Retrieves or initializes the frozen production model loader."""
        if cls._cached_loader is None:
            try:
                final_dir = os.path.join(settings.PROJECT_ROOT, "models", "ri", "final")
                cls._cached_loader = FrozenModelLoader(artifact_dir=final_dir)
            except FrozenModelLoadError as e:
                logger.error(f"Failed to load frozen production model: {e}")
                raise ModelUnavailableError(f"Frozen production model is unavailable: {str(e)}") from e
            except Exception as e:
                logger.error(f"Unexpected error loading frozen production model: {e}")
                raise ModelUnavailableError(f"Frozen production model could not be initialized: {str(e)}") from e
        return cls._cached_loader

    @classmethod
    def _get_historical_samples(cls) -> List[Any]:
        """Lazy loads verified historical samples from EnvironmentalRIDatasetBuilder."""
        if cls._cached_historical_samples is None:
            try:
                from ml.datasets.environmental_ri_dataset import EnvironmentalRIDatasetBuilder
                builder = EnvironmentalRIDatasetBuilder(project_root=settings.PROJECT_ROOT)
                dataset = builder.build()
                cls._cached_historical_samples = dataset.samples
            except Exception as e:
                logger.warning(f"Could not load historical dataset builder: {e}")
                cls._cached_historical_samples = []
        return cls._cached_historical_samples

    def predict_observation(
        self,
        request: PredictionRequest,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        persist: bool = True,
    ) -> PredictionResponse:
        """
        Executes frozen model inference for a submitted observation.
        """
        # 1. Determine feature vector
        features_dict: Dict[str, Any] = {}
        historical_match = None

        if request.temporal_features and request.spatial_features:
            # Client provided explicit feature dictionaries
            try:
                features_dict = InferenceFeatureContract.assemble_contract_vector(
                    temporal_dict=request.temporal_features,
                    spatial_dict=request.spatial_features,
                )
            except FeatureContractViolationError as e:
                raise FeatureContractInvalidError(
                    message=str(e),
                    details={
                        "missing_features": e.missing_features,
                        "invalid_types": e.invalid_types,
                        "forbidden_features": e.forbidden_features,
                    },
                ) from e
        else:
            # Attempt to locate observation in verified historical dataset
            historical_match = self._find_historical_sample(
                storm_id=request.storm_id,
                storm_name=request.storm_name,
                observation_time_utc=request.observation_time_utc,
            )

            if historical_match is not None:
                try:
                    features_dict = InferenceFeatureContract.assemble_contract_vector(
                        temporal_dict=historical_match.temporal_features,
                        spatial_dict=historical_match.spatial_features,
                    )
                except FeatureContractViolationError as e:
                    raise FeatureContractInvalidError(
                        message=f"Historical record contract error: {str(e)}",
                        details={"missing_features": e.missing_features},
                    ) from e
            elif request.latitude is not None and request.longitude is not None and (request.current_wind_kts is not None or request.wind_speed_kts is not None):
                # Construct feature contract vector from observational kinematics with unobserved satellite indicators
                wind = float(request.current_wind_kts if request.current_wind_kts is not None else request.wind_speed_kts)
                temp_dict: Dict[str, Any] = {
                    "track_latitude_val": float(request.latitude),
                    "track_latitude_is_observed": 1.0,
                    "track_longitude_val": float(request.longitude),
                    "track_longitude_is_observed": 1.0,
                    "track_wind_speed_val": wind,
                    "track_wind_speed_is_observed": 1.0,
                    "track_pressure_val": float(request.central_pressure_mb) if request.central_pressure_mb is not None else np.nan,
                    "track_pressure_is_observed": 1.0 if request.central_pressure_mb is not None else 0.0,
                    "track_translation_speed_kts_val": np.nan,
                    "track_translation_speed_kts_is_observed": 0.0,
                    "track_translation_bearing_deg_val": np.nan,
                    "track_translation_bearing_deg_is_observed": 0.0,
                    "temp_delta_wind_6h_val": float(wind - request.prev_wind_speed_kts) if request.prev_wind_speed_kts is not None else np.nan,
                    "temp_delta_wind_6h_is_observed": 1.0 if request.prev_wind_speed_kts is not None else 0.0,
                    "temp_delta_wind_12h_val": np.nan,
                    "temp_delta_wind_12h_is_observed": 0.0,
                    "temp_delta_pressure_6h_val": np.nan,
                    "temp_delta_pressure_6h_is_observed": 0.0,
                    "temp_wind_change_rate_per_hour_val": float((wind - request.prev_wind_speed_kts) / 6.0) if request.prev_wind_speed_kts is not None else np.nan,
                    "temp_wind_change_rate_per_hour_is_observed": 1.0 if request.prev_wind_speed_kts is not None else 0.0,
                    "temp_delta_ir_min_6h_val": np.nan,
                    "temp_delta_ir_min_6h_is_observed": 0.0,
                    "quality_track_available": 1.0,
                }
                from ml.inference.feature_contract import CANONICAL_SPATIAL_FEATURES
                spat_dict: Dict[str, Any] = {
                    f: np.nan for f in CANONICAL_SPATIAL_FEATURES
                }
                spat_dict["has_irwvp"] = 0.0
                spat_dict["has_vschn"] = 0.0
                features_dict = InferenceFeatureContract.assemble_contract_vector(temp_dict, spat_dict)
            else:
                # If neither explicit features nor historical match is available, fail loudly
                raise FeatureContractInvalidError(
                    message=(
                        f"Observation for storm '{request.storm_name or request.storm_id}' does not contain required coordinates and winds, "
                        "and was not found in the verified historical catalog. Cannot generate prediction without real inputs."
                    ),
                    details={"error_code": "FEATURE_CONTRACT_INVALID"},
                )

        # 2. Invoke frozen model
        try:
            inference_result = self.model_loader.predict_from_feature_dict(
                features=features_dict,
                threshold_override=request.threshold_override,
            )
        except FrozenModelSchemaMismatchError as e:
            raise FeatureContractInvalidError(message=str(e)) from e
        except FrozenModelInferenceError as e:
            raise PredictionFailedError(message=str(e)) from e
        except Exception as e:
            raise PredictionFailedError(message=f"Model evaluation encountered an error: {str(e)}") from e

        # 3. Assemble provenance
        obs_time = request.observation_time_utc or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        provenance = DataProvenance(
            track_dataset="NOAA IBTrACS v04r01 (WMO verified track points)",
            satellite_dataset="NOAA HURSAT-B1 v06 (3-hourly geostationary IR & WV netCDF)",
            observation_time_utc=obs_time,
            cyclone_center_lat=float(request.latitude),
            cyclone_center_lon=float(request.longitude),
            temporal_match_offset_minutes=0.0,
        )

        # 4. Satellite channel availability
        has_wv = bool(features_dict.get("has_irwvp", 0.0) >= 0.5)
        has_vis = bool(features_dict.get("has_vschn", 0.0) >= 0.5)
        has_ir = bool(historical_match is not None or (request.spatial_features is not None and not np.isnan(features_dict.get("irwin_mean", np.nan))))
        channels = []
        if has_ir:
            channels.append("IRWIN")
        if has_wv:
            channels.append("IRWVP")
        if has_vis:
            channels.append("VSCHN")
        satellite_available = bool(len(channels) > 0)

        # 5. Build response object
        top_supporting = [
            FeatureAttributionItem(
                feature_name=item["feature_name"],
                attribution_score=item["attribution_score"],
                direction=item["direction"],
                model_coefficient=item.get("model_coefficient"),
                raw_value=item.get("raw_value"),
            )
            for item in inference_result.get("top_supporting_features", [])
        ]

        top_suppressing = [
            FeatureAttributionItem(
                feature_name=item["feature_name"],
                attribution_score=item["attribution_score"],
                direction=item["direction"],
                model_coefficient=item.get("model_coefficient"),
                raw_value=item.get("raw_value"),
            )
            for item in inference_result.get("top_suppressing_features", [])
        ]

        limitations = [
            "Dataset scale restricted to 6 unique historical North Indian Ocean cyclone lifecycles (299 supervised samples, 39 RI+).",
            "Spatial structure requires geostationary infrared satellite patch availability contemporaneous with cyclone fix.",
            "Conservative thresholding yields high precision (0 false alarms on Chapala) but lower recall on asymmetric early-stage intensification.",
            "Not certified as an autonomous warning issuer; official IMD / JTWC meteorological warnings remain authoritative.",
            "Deep learning architectures and environmental features are not part of the frozen production model.",
        ]

        if not satellite_available:
            limitations.append("Coincident infrared satellite imagery is absent; prediction is operating exclusively on track kinematics.")

        disclaimers = [
            "This is a model-derived empirical RI risk index, not an official meteorological warning or calibrated probability.",
            "Official meteorological warnings remain authoritative.",
            "Rapid Intensification is defined strictly as maximum sustained 1-minute wind speed increase >= 30 kts within 24 hours.",
            "Standardized linear feature attributions reflect statistical model weights within the linear model and do not establish physical causation.",
        ]

        # 6. Prediction Record Persistence
        db_id = None
        created_time = datetime.now(timezone.utc)

        if self.db is not None and persist:
            try:
                obs_dt = None
                try:
                    obs_dt = datetime.fromisoformat(obs_time.replace("Z", "+00:00"))
                except Exception:
                    obs_dt = created_time

                pred_record = Prediction(
                    cyclone_id=(request.storm_id or "UNKNOWN")[:36],
                    storm_id=request.storm_id,
                    storm_name=request.storm_name or "UNNAMED",
                    observation_time=obs_dt,
                    prediction_time=created_time,
                    model_name=self.model_loader.EXPECTED_MODEL_NAME,
                    model_version=self.model_loader.EXPECTED_VERSION,
                    ri_risk_index=inference_result["ri_risk_index"],
                    operating_threshold=inference_result["operating_threshold"],
                    ri_flag=inference_result["ri_flag"],
                    risk_category=inference_result["risk_category"],
                    forecast_horizon_hours=24.0,
                    temporal_evidence_available=True,
                    satellite_evidence_available=satellite_available,
                    satellite_channels=channels,
                    input_provenance=provenance.model_dump(),
                    explanation_metadata={
                        "top_supporting": [item.model_dump() for item in top_supporting],
                        "top_suppressing": [item.model_dump() for item in top_suppressing],
                    },
                    requested_by=user_email or user_id or "system",
                    # Backwards compatibility legacy fields
                    ri_probability_24h=inference_result["ri_risk_index"],
                    ri_risk_level=inference_result["risk_category"],
                    estimated_vmax_knots=request.current_wind_kts,
                    estimated_mslp_hpa=request.central_pressure_mb,
                )
                self.db.add(pred_record)
                self.db.commit()
                self.db.refresh(pred_record)
                db_id = pred_record.id

                # Audit Log Recording
                audit_service = AuditService(self.db)
                audit_service.record_event(
                    action="GENERATE_PREDICTION",
                    resource_type="prediction",
                    resource_id=db_id,
                    user_id=user_id,
                    metadata={
                        "storm_id": request.storm_id,
                        "storm_name": request.storm_name,
                        "model_version": self.model_loader.EXPECTED_VERSION,
                        "ri_risk_index": inference_result["ri_risk_index"],
                        "risk_category": inference_result["risk_category"],
                        "observation_time": obs_time,
                        "provenance_track": provenance.track_dataset,
                        "provenance_satellite": provenance.satellite_dataset,
                    },
                )
            except Exception as e:
                logger.error(f"Failed to persist prediction record: {e}")
                self.db.rollback()

        pred_id = db_id or f"pred-{int(created_time.timestamp())}"

        return PredictionResponse(
            prediction_id=pred_id,
            storm_id=request.storm_id,
            storm_name=request.storm_name or "UNNAMED",
            observation_time_utc=obs_time,
            model_name=self.model_loader.EXPECTED_MODEL_NAME,
            model_version=self.model_loader.EXPECTED_VERSION,
            ri_risk_index=inference_result["ri_risk_index"],
            operating_threshold=inference_result["operating_threshold"],
            ri_flag=inference_result["ri_flag"],
            risk_category=inference_result["risk_category"],
            forecast_horizon_hours=24.0,
            ri_definition="Maximum sustained 1-minute wind speed increase >= 30 kts in 24 hours (V_t+24h - V_t >= 30 kts)",
            temporal_evidence_available=True,
            satellite_evidence_available=satellite_available,
            satellite_channels_available=channels,
            input_data_timestamp=obs_time,
            input_data_provenance=provenance,
            model_status="Frozen Production Model (Sprint 11 Multi-Storm Certified)",
            calibration_status="Uncalibrated Model Score (Empirical Risk Index; Platt scaling unvalidated due to sample scale)",
            top_supporting_features=top_supporting,
            top_suppressing_features=top_suppressing,
            limitations=limitations,
            disclaimers=disclaimers,
            created_at=created_time,
        )

    def get_prediction_by_id(self, prediction_id: str) -> PredictionResponse:
        """Retrieves a stored prediction by its unique identifier."""
        if self.db is None:
            raise NotFoundError(message=f"Prediction '{prediction_id}' not found (Database disconnected).")

        record = self.db.query(Prediction).filter(Prediction.id == prediction_id).first()
        if not record:
            raise NotFoundError(message=f"Prediction '{prediction_id}' not found.")

        return self._record_to_response(record)

    def list_predictions(
        self,
        storm_id: Optional[str] = None,
        storm_name: Optional[str] = None,
        risk_category: Optional[str] = None,
        model_version: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[PredictionResponse], int]:
        """Lists historical prediction records with optional filtering."""
        if self.db is None:
            return [], 0

        query = self.db.query(Prediction)
        if storm_id:
            query = query.filter(Prediction.storm_id == storm_id)
        if storm_name:
            query = query.filter(Prediction.storm_name.ilike(f"%{storm_name}%"))
        if risk_category:
            query = query.filter(Prediction.risk_category == risk_category)
        if model_version:
            query = query.filter(Prediction.model_version == model_version)

        total = query.count()
        records = query.order_by(Prediction.created_at.desc()).offset(skip).limit(limit).all()
        return [self._record_to_response(r) for r in records], total

    def predict_historical_storm(
        self,
        storm_id_or_name: str,
        threshold_override: Optional[float] = None,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        persist: bool = True,
    ) -> PredictionResponse:
        """
        Executes prediction for a known historical storm by selecting its peak verified observation.
        """
        samples = self._get_historical_samples()
        matching = [
            s for s in samples
            if s.storm_name.upper() == storm_id_or_name.upper()
            or s.storm_id.upper() == storm_id_or_name.upper()
        ]

        if not matching:
            raise ObservationNotFoundError(
                message=f"Storm '{storm_id_or_name}' not found in verified historical observation catalog."
            )

        # Pick peak intensity or primary RI sample
        ri_positives = [s for s in matching if getattr(s, "ri_target", 0) == 1]
        chosen_sample = ri_positives[0] if ri_positives else matching[len(matching) // 2]

        request = PredictionRequest(
            storm_id=chosen_sample.storm_id,
            storm_name=chosen_sample.storm_name,
            observation_time_utc=chosen_sample.observation_time,
            latitude=chosen_sample.latitude,
            longitude=chosen_sample.longitude,
            current_wind_kts=chosen_sample.current_wind_kts or 50.0,
            temporal_features=chosen_sample.temporal_features,
            spatial_features=chosen_sample.spatial_features,
            threshold_override=threshold_override,
        )

        return self.predict_observation(
            request=request,
            user_id=user_id,
            user_email=user_email,
            persist=persist,
        )

    def _find_historical_sample(
        self,
        storm_id: Optional[str],
        storm_name: Optional[str],
        observation_time_utc: str,
    ) -> Optional[Any]:
        """Looks up a specific sample in the verified historical catalog."""
        samples = self._get_historical_samples()
        norm_time = observation_time_utc.replace("Z", "+00:00")[:16]

        for s in samples:
            name_match = (
                (storm_name and s.storm_name.upper() == storm_name.upper()) or
                (storm_id and (s.storm_id.upper() == storm_id.upper() or s.storm_name.upper() == storm_id.upper()))
            )
            if name_match:
                s_time = s.observation_time.replace("Z", "+00:00")[:16]
                if s_time == norm_time:
                    return s

        # Fallback to closest or matching storm if only storm name was given
        for s in samples:
            if (storm_name and s.storm_name.upper() == storm_name.upper()) or (storm_id and s.storm_id.upper() == storm_id.upper()):
                return s

        return None

    def _record_to_response(self, record: Prediction) -> PredictionResponse:
        """Converts an ORM Prediction instance into a PredictionResponse schema."""
        provenance_dict = record.input_provenance or {}
        provenance = DataProvenance(
            track_dataset=provenance_dict.get("track_dataset", "NOAA IBTrACS v04r01"),
            satellite_dataset=provenance_dict.get("satellite_dataset", "NOAA HURSAT-B1 v06"),
            observation_time_utc=provenance_dict.get("observation_time_utc", record.observation_time.isoformat() if record.observation_time else "UNKNOWN"),
            cyclone_center_lat=float(provenance_dict.get("cyclone_center_lat", 0.0)),
            cyclone_center_lon=float(provenance_dict.get("cyclone_center_lon", 0.0)),
            temporal_match_offset_minutes=float(provenance_dict.get("temporal_match_offset_minutes", 0.0)),
        )

        explanation = record.explanation_metadata or {}
        top_supporting = [
            FeatureAttributionItem(**item) for item in explanation.get("top_supporting", [])
        ]
        top_suppressing = [
            FeatureAttributionItem(**item) for item in explanation.get("top_suppressing", [])
        ]

        obs_time_str = record.observation_time.isoformat() if record.observation_time else "UNKNOWN"

        limitations = [
            "Dataset scale restricted to 6 unique historical North Indian Ocean cyclone lifecycles (299 supervised samples, 39 RI+).",
            "Spatial structure requires geostationary infrared satellite patch availability contemporaneous with cyclone fix.",
            "Conservative thresholding yields high precision (0 false alarms on Chapala) but lower recall on asymmetric early-stage intensification.",
            "Not certified as an autonomous warning issuer; official IMD / JTWC meteorological warnings remain authoritative.",
            "Deep learning architectures and environmental features are not part of the frozen production model.",
        ]

        disclaimers = [
            "This is a model-derived empirical RI risk index, not an official meteorological warning or calibrated probability.",
            "Official meteorological warnings remain authoritative.",
            "Rapid Intensification is defined strictly as maximum sustained 1-minute wind speed increase >= 30 kts within 24 hours.",
            "Standardized linear feature attributions reflect statistical model weights within the linear model and do not establish physical causation.",
        ]

        return PredictionResponse(
            prediction_id=record.id,
            storm_id=record.storm_id or "UNKNOWN",
            storm_name=record.storm_name or "UNNAMED",
            observation_time_utc=obs_time_str,
            model_name=record.model_name or "CycloneGuard-RI-Multimodal-TS-Final",
            model_version=record.model_version or "v3.0.0-frozen",
            ri_risk_index=round(float(record.ri_risk_index), 4),
            operating_threshold=round(float(record.operating_threshold), 3),
            ri_flag=bool(record.ri_flag),
            risk_category=record.risk_category or "LOW_RISK",
            forecast_horizon_hours=float(record.forecast_horizon_hours or 24.0),
            ri_definition="Maximum sustained 1-minute wind speed increase >= 30 kts in 24 hours",
            temporal_evidence_available=bool(record.temporal_evidence_available),
            satellite_evidence_available=bool(record.satellite_evidence_available),
            satellite_channels_available=record.satellite_channels or ["IRWIN", "IRWVP"],
            input_data_timestamp=obs_time_str,
            input_data_provenance=provenance,
            model_status="Frozen Production Model (Sprint 11 Multi-Storm Certified)",
            calibration_status="Uncalibrated Empirical Risk Index (Platt scaling unvalidated due to sample scale)",
            top_supporting_features=top_supporting,
            top_suppressing_features=top_suppressing,
            limitations=limitations,
            disclaimers=disclaimers,
            created_at=record.created_at,
        )
