"""
Historical Case Study Service (Sprint 13).

Provides end-to-end evidence pipelines for historical tropical cyclone reanalysis.
Strict Scientific Guardrails:
1. Zero lookahead: Future ground truth (future_wind, delta_wind, ri_target) is strictly
   isolated in HistoricalOutcomeVerification and NEVER passed into feature vectors or inference.
2. Labeling integrity: 'Empirical RI Risk Index' (operating threshold tau = 0.125).
3. Attribution integrity: 'Model Feature Attribution' (statistical contribution, not physical causality).
4. Real data only: Real HURSAT-B1 spatial structural features and IBTrACS kinematic features.
"""

from datetime import datetime, timedelta, timezone
import io
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from PIL import Image
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import NotFoundError, ObservationNotFoundError
from app.models.cyclone import Cyclone
from app.schemas.case_study import (
    AttributionEntry,
    CaseStudyResponse,
    HistoricalOutcomeVerification,
    ModelFeatureAttributionSummary,
    ModelScoreSummary,
    SatelliteStructuralEvidenceSummary,
    TemporalIndicatorsSummary,
    TimelineObservationItem,
    WhatTheModelSaw,
)
from app.schemas.prediction import PredictionRequest
from app.services.prediction.service import PredictionService
from ml.datasets.spatial_ri_dataset import SpatialRIDatasetBuilder

logger = logging.getLogger("cycloneguard.case_study_service")

# Human-readable translations for feature names
FEATURE_DISPLAY_NAMES: Dict[str, str] = {
    "track_wind_speed_val": "Current Intensity (Vmax)",
    "temp_delta_wind_12h_val": "12-Hour Prior Intensity Change (ΔV12)",
    "temp_delta_wind_6h_val": "6-Hour Prior Intensity Change (ΔV6)",
    "track_pressure_val": "Central Minimum Pressure (MSLP)",
    "temp_delta_pressure_6h_val": "6-Hour Pressure Tendency (ΔP6)",
    "temp_wind_change_rate_per_hour_val": "Hourly Intensification Acceleration",
    "track_translation_speed_kts_val": "Vortex Translation Speed",
    "track_translation_bearing_deg_val": "Track Motion Bearing",
    "irwin_min": "Deep Convective Minimum Temperature (IRWIN Min Tb)",
    "irwin_core_mean": "Inner Core Brightness Temperature (Core Mean Tb)",
    "irwin_cold_cloud_fraction_233k": "Deep Convection Cold Cloud Area (<233K)",
    "irwin_very_cold_cloud_fraction_219k": "Vigorous Convective Area (<219K)",
    "irwin_overshooting_fraction_203k": "Overshooting Convective Top Fraction (<203K)",
    "irwin_core_ring_diff": "Inner Core vs Outer Ring Temperature Gradient",
    "irwin_azimuthal_std_core": "Azimuthal Convective Asymmetry (Core Std)",
    "irwvp_mean": "Upper-Tropospheric Water Vapor Brightness Temp",
    "ir_wv_diff_mean": "IR-WV Channel Radiative Difference",
    "ir_wv_spatial_corr": "IR-WV Multichannel Structural Alignment",
    "track_latitude_val": "Geographic Latitude",
    "track_longitude_val": "Geographic Longitude",
}

CANONICAL_OBSERVATIONS: Dict[str, str] = {
    "2015301N11065": "2015-10-28T18:00:00Z",  # Chapala RI+ onset
    "CHAPALA": "2015-10-28T18:00:00Z",
    "2014297N11062": "2014-10-23T12:00:00Z",  # Nilofar non-RI baseline
    "NILOFAR": "2014-10-23T12:00:00Z",
    "2013281N12098": "2013-10-09T00:00:00Z",  # Phailin RI phase
    "PHAILIN": "2013-10-09T00:00:00Z",
    "2013322N13090": "2013-11-18T00:00:00Z",  # Helen non-RI
    "HELEN": "2013-11-18T00:00:00Z",
    "2014279N11096": "2014-10-08T00:00:00Z",  # Hudhud
    "HUDHUD": "2014-10-08T00:00:00Z",
    "2015309N14067": "2015-11-05T00:00:00Z",  # Megh
    "MEGH": "2015-11-05T00:00:00Z",
}


def _bearing_to_heading(deg: Optional[float]) -> Optional[str]:
    if deg is None or np.isnan(deg):
        return None
    deg = deg % 360
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    idx = int((deg + 11.25) / 22.5) % 16
    return directions[idx]


class CaseStudyService:
    """Encapsulates historical case study and evidence extraction."""

    _cached_samples: Optional[List[Any]] = None

    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self.prediction_service = PredictionService(db=db)

    @classmethod
    def _get_samples(cls) -> List[Any]:
        if cls._cached_samples is None:
            builder = SpatialRIDatasetBuilder(project_root=settings.PROJECT_ROOT)
            ds = builder.build()
            cls._cached_samples = ds.samples
            logger.info(f"Loaded {len(ds.samples)} verified historical samples into CaseStudyService.")
        return cls._cached_samples

    def get_storm_samples(self, storm_id_or_name: str) -> List[Any]:
        samples = self._get_samples()
        query = storm_id_or_name.strip().upper()
        matching = [
            s for s in samples
            if s.storm_id.upper() == query or s.storm_name.upper() == query
        ]
        if not matching:
            raise NotFoundError(message=f"Historical cyclone '{storm_id_or_name}' not found in verified dataset.")
        # Sort chronologically
        matching.sort(key=lambda s: s.observation_time)
        return matching

    def get_timeline(self, storm_id_or_name: str) -> List[TimelineObservationItem]:
        """Returns chronological observation timeline with pre-computed RI risk indices."""
        samples = self.get_storm_samples(storm_id_or_name)
        storm_id = samples[0].storm_id
        canonical_time = CANONICAL_OBSERVATIONS.get(storm_id, CANONICAL_OBSERVATIONS.get(samples[0].storm_name, samples[0].observation_time))

        timeline_items: List[TimelineObservationItem] = []
        for s in samples:
            src_avail = s.source_availability or {}
            has_irwin = bool(src_avail.get("has_irwin", 1.0))
            has_irwvp = bool(src_avail.get("has_irwvp", 0.0))
            has_vschn = bool(src_avail.get("has_vschn", 0.0))
            channels = []
            if has_irwin:
                channels.append("IRWIN")
            if has_irwvp:
                channels.append("IRWVP")
            if has_vschn:
                channels.append("VSCHN")

            obs_id = s.observation_time.replace("-", "").replace(":", "")

            # Calculate fast inference score for the timeline point
            ri_risk_index = None
            ri_flag = None
            risk_category = None
            try:
                pred_req = PredictionRequest(
                    storm_id=s.storm_id,
                    storm_name=s.storm_name,
                    observation_time_utc=s.observation_time,
                    latitude=s.latitude,
                    longitude=s.longitude,
                    current_wind_kts=s.current_wind_kts,
                    temporal_features=s.temporal_features,
                    spatial_features=s.spatial_features,
                )
                pred_res = self.prediction_service.predict_observation(pred_req, persist=False)
                ri_risk_index = pred_res.ri_risk_index
                ri_flag = pred_res.ri_flag
                risk_category = pred_res.risk_category
            except Exception as e:
                logger.debug(f"Quick inference skipped for {s.observation_time}: {e}")

            timeline_items.append(
                TimelineObservationItem(
                    observation_id=obs_id,
                    observation_time=s.observation_time,
                    storm_id=s.storm_id,
                    storm_name=s.storm_name,
                    latitude=round(s.latitude, 2),
                    longitude=round(s.longitude, 2),
                    current_wind_kts=float(s.current_wind_kts or 0.0),
                    central_pressure_mb=float(s.temporal_features.get("track_pressure_val")) if s.temporal_features.get("track_pressure_val") is not None else None,
                    has_irwin=has_irwin,
                    has_irwvp=has_irwvp,
                    has_vschn=has_vschn,
                    satellite_channels=channels,
                    ri_risk_index=ri_risk_index,
                    operating_threshold=0.125,
                    ri_flag=ri_flag,
                    risk_category=risk_category,
                    source_status="NOAA IBTrACS + HURSAT-B1 Verified",
                    is_canonical=(s.observation_time == canonical_time),
                )
            )

        return timeline_items

    def get_case_study(
        self,
        storm_id_or_name: str,
        observation_time_utc: Optional[str] = None,
    ) -> CaseStudyResponse:
        """
        Builds the complete historical case study with strict separation between
        'WHAT THE MODEL SAW' and 'HISTORICAL OUTCOME'.
        """
        samples = self.get_storm_samples(storm_id_or_name)
        first_sample = samples[0]
        storm_id = first_sample.storm_id
        storm_name = first_sample.storm_name

        canonical_time = CANONICAL_OBSERVATIONS.get(storm_id, CANONICAL_OBSERVATIONS.get(storm_name, first_sample.observation_time))
        target_time = observation_time_utc if observation_time_utc else canonical_time

        # Match observation
        selected_sample = None
        for s in samples:
            if s.observation_time[:16] == target_time[:16]:
                selected_sample = s
                break
        if selected_sample is None:
            # Fallback to canonical or first
            selected_sample = next((s for s in samples if s.observation_time[:16] == canonical_time[:16]), samples[0])

        # Run model inference on selected sample (ONLY observation-time inputs)
        pred_req = PredictionRequest(
            storm_id=selected_sample.storm_id,
            storm_name=selected_sample.storm_name,
            observation_time_utc=selected_sample.observation_time,
            latitude=selected_sample.latitude,
            longitude=selected_sample.longitude,
            current_wind_kts=selected_sample.current_wind_kts,
            temporal_features=selected_sample.temporal_features,
            spatial_features=selected_sample.spatial_features,
        )
        pred = self.prediction_service.predict_observation(pred_req, persist=True)

        # Assemble SECTION A: WHAT THE MODEL SAW
        tf = selected_sample.temporal_features or {}
        sf = selected_sample.spatial_features or {}
        src_avail = selected_sample.source_availability or {}

        # 1. Temporal indicators summary
        v_speed = tf.get("track_translation_speed_kts_val")
        v_bearing = tf.get("track_translation_bearing_deg_val")
        temporal_summary = TemporalIndicatorsSummary(
            current_wind_kts=float(selected_sample.current_wind_kts or 0.0),
            wind_change_6h_kts=float(tf.get("temp_delta_wind_6h_val")) if tf.get("temp_delta_wind_6h_val") is not None else None,
            wind_change_12h_kts=float(tf.get("temp_delta_wind_12h_val")) if tf.get("temp_delta_wind_12h_val") is not None else None,
            central_pressure_mb=float(tf.get("track_pressure_val")) if tf.get("track_pressure_val") is not None else None,
            pressure_drop_6h_mb=float(tf.get("temp_delta_pressure_6h_val")) if tf.get("temp_delta_pressure_6h_val") is not None else None,
            translation_speed_kts=round(float(v_speed), 2) if v_speed is not None else None,
            translation_bearing_deg=round(float(v_bearing), 1) if v_bearing is not None else None,
            translation_heading=_bearing_to_heading(v_bearing),
            source_label="Derived from observation history (NOAA IBTrACS best-track sequence)",
        )

        # 2. Satellite structural evidence summary
        has_irwin = bool(src_avail.get("has_irwin", 1.0))
        has_irwvp = bool(src_avail.get("has_irwvp", 0.0))
        has_vschn = bool(src_avail.get("has_vschn", 0.0))
        channels = []
        if has_irwin:
            channels.append("IRWIN")
        if has_irwvp:
            channels.append("IRWVP")
        if has_vschn:
            channels.append("VSCHN")

        norm_time_id = selected_sample.observation_time.replace("-", "").replace(":", "")[:16]
        img_endpoint = f"/api/v1/cyclones/{storm_id}/observations/{norm_time_id}/patch/IRWIN"

        satellite_summary = SatelliteStructuralEvidenceSummary(
            source="NOAA HURSAT-B1 Geostationary Infrared",
            channels_available=channels,
            has_irwin=has_irwin,
            has_irwvp=has_irwvp,
            has_vschn=has_vschn,
            irwin_mean_tb_k=round(float(sf.get("irwin_mean")), 2) if sf.get("irwin_mean") is not None else None,
            irwin_min_tb_k=round(float(sf.get("irwin_min")), 2) if sf.get("irwin_min") is not None else None,
            cold_cloud_fraction_233k=round(float(sf.get("irwin_cold_cloud_fraction_233k")), 4) if sf.get("irwin_cold_cloud_fraction_233k") is not None else None,
            very_cold_cloud_fraction_219k=round(float(sf.get("irwin_very_cold_cloud_fraction_219k")), 4) if sf.get("irwin_very_cold_cloud_fraction_219k") is not None else None,
            overshooting_top_fraction_203k=round(float(sf.get("irwin_overshooting_fraction_203k")), 4) if sf.get("irwin_overshooting_fraction_203k") is not None else None,
            core_convection_mean_k=round(float(sf.get("irwin_core_mean")), 2) if sf.get("irwin_core_mean") is not None else None,
            core_ring_temperature_diff_k=round(float(sf.get("irwin_core_ring_diff")), 2) if sf.get("irwin_core_ring_diff") is not None else None,
            azimuthal_symmetry_metric=round(float(sf.get("irwin_azimuthal_std_core")), 4) if sf.get("irwin_azimuthal_std_core") is not None else None,
            imagery_endpoint=img_endpoint,
        )

        # 3. Model score summary
        model_score = ModelScoreSummary(
            model_name="CycloneGuard-RI-Multimodal-TS-Final",
            model_version="v3.0.0-frozen",
            ri_risk_index=pred.ri_risk_index,
            operating_threshold=pred.operating_threshold,
            ri_flag=pred.ri_flag,
            risk_category=pred.risk_category,
            forecast_horizon_hours=24.0,
            score_label="Empirical RI Risk Index",
            threshold_label="Operating Decision Threshold (τ = 0.125)",
            calibration_status="Uncalibrated Empirical Index",
        )

        # 4. Model feature attribution summary
        def map_attributions(items: List[Any], direction_label: str) -> List[AttributionEntry]:
            entries = []
            for item in items:
                fname = item.feature_name
                dname = FEATURE_DISPLAY_NAMES.get(fname, fname)
                score = float(item.attribution_score)
                note = (
                    "This feature contributed positively to the empirical model score."
                    if score > 0 else
                    "This feature dampened the empirical model score."
                )
                entries.append(
                    AttributionEntry(
                        feature_name=fname,
                        display_name=dname,
                        direction=direction_label,
                        attribution_score=round(score, 4),
                        contribution_magnitude=round(abs(score), 4),
                        normalized_value=round(float(item.raw_value), 4) if getattr(item, "raw_value", None) is not None else None,
                        explanation_note=note,
                    )
                )
            return entries

        attribution_summary = ModelFeatureAttributionSummary(
            title="Model Feature Attribution",
            method="Standardized Linear Coefficient Weighting",
            top_supporting_features=map_attributions(pred.top_supporting_features or [], "supports_ri"),
            top_suppressing_features=map_attributions(pred.top_suppressing_features or [], "suppresses_ri"),
            attribution_disclaimer="Attributions describe statistical model behavior within the regularized linear decision space, not physical meteorological causality.",
        )

        what_the_model_saw = WhatTheModelSaw(
            observation_time_utc=selected_sample.observation_time,
            storm_id=selected_sample.storm_id,
            storm_name=selected_sample.storm_name,
            latitude=round(selected_sample.latitude, 2),
            longitude=round(selected_sample.longitude, 2),
            temporal_indicators=temporal_summary,
            temporal_features={k: float(v) for k, v in tf.items() if v is not None and not np.isnan(v)},
            satellite_evidence=satellite_summary,
            spatial_features={k: float(v) for k, v in sf.items() if v is not None and not np.isnan(v)},
            model_score=model_score,
            model_feature_attribution=attribution_summary,
        )

        # Assemble SECTION B: HISTORICAL OUTCOME (STRICTLY ISOLATED)
        try:
            obs_dt = datetime.fromisoformat(selected_sample.observation_time.replace("Z", "+00:00"))
            verif_dt = obs_dt + timedelta(hours=24)
            verif_time_str = verif_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except Exception:
            verif_time_str = f"{selected_sample.observation_time} + 24h"

        fut_wind = float(getattr(selected_sample, "future_wind_kts", 0.0) or 0.0)
        delta_wind = float(getattr(selected_sample, "delta_wind_kts", 0.0) or 0.0)
        ri_occ = bool(getattr(selected_sample, "ri_target", 0) == 1)

        historical_outcome = HistoricalOutcomeVerification(
            title="HISTORICAL OUTCOME — NOT USED AS MODEL INPUT",
            observation_time=selected_sample.observation_time,
            verification_time_24h=verif_time_str,
            observed_future_wind_kts=fut_wind,
            observed_delta_v_24h=delta_wind,
            ri_occurred=ri_occ,
            wmo_ri_criterion="Maximum sustained 1-minute wind speed increase >= 30 kts in 24 hours",
            disclaimer="Ground truth verified from NOAA IBTrACS historical reanalysis. This information represents future state (t + 24h) and was strictly hidden from model inference.",
        )

        # Compute lifecycle metrics
        winds = [float(s.current_wind_kts) for s in samples if s.current_wind_kts is not None]
        pressures = [
            float(s.temporal_features["track_pressure_val"])
            for s in samples
            if s.temporal_features and s.temporal_features.get("track_pressure_val") is not None
        ]
        ri_events = sum(1 for s in samples if getattr(s, "ri_target", 0) == 1)

        # Get cyclone DB record for metadata if available
        cyclone_record = None
        if self.db:
            cyclone_record = self.db.query(Cyclone).filter(
                (Cyclone.id == storm_id) | (Cyclone.name == storm_name)
            ).first()

        summary_text = cyclone_record.notes if cyclone_record and cyclone_record.notes else (
            f"Historical cyclone {storm_name} reanalysis benchmark in the North Indian Ocean basin. "
            f"Evaluated across {len(samples)} coincident observations."
        )

        timeline = self.get_timeline(storm_id)

        limitations = [
            "Dataset scale restricted to 6 unique historical North Indian Ocean cyclone lifecycles (299 supervised samples, 39 RI+).",
            "Empirical RI risk index is uncalibrated; Platt scaling was unvalidated due to sample size constraints.",
            "Attributions reflect regularized linear decision boundaries, not physical or dynamical meteorological causality.",
            "Zero lookahead verified: Future 24h ground truth was strictly excluded from prediction-time feature vectors.",
            "Official IMD/JTWC/RSMC meteorological warnings remain authoritative over automated AI research models.",
        ]

        return CaseStudyResponse(
            storm_id=storm_id,
            storm_name=storm_name,
            basin="North Indian Ocean",
            international_id=cyclone_record.international_id if cyclone_record else "BENCHMARK-NIO",
            summary=summary_text,
            lifecycle_start_utc=samples[0].observation_time,
            lifecycle_end_utc=samples[-1].observation_time,
            peak_intensity_kts=max(winds) if winds else 0.0,
            min_central_pressure_mb=min(pressures) if pressures else None,
            total_verified_observations=len(samples),
            ri_events_count=ri_events,
            canonical_observation_time_utc=canonical_time,
            selected_observation_time_utc=selected_sample.observation_time,
            timeline=timeline,
            what_the_model_saw=what_the_model_saw,
            historical_outcome=historical_outcome,
            scientific_limitations=limitations,
            authoritative_warning_advisory="Official meteorological warnings from IMD / JTWC remain authoritative.",
        )

    def render_satellite_patch_png(
        self,
        storm_id_or_name: str,
        observation_id: str,
        channel: str = "IRWIN",
    ) -> Optional[bytes]:
        """
        Renders an authentic PNG image from the real NOAA HURSAT-B1 64x64 numpy array.
        Zero synthetic imagery; 100% genuine historical observational data.
        """
        samples = self.get_storm_samples(storm_id_or_name)
        storm_id = samples[0].storm_id

        # Normalize observation timestamp to directory format (e.g. 20151028T180000Z)
        norm_obs = observation_id.replace("-", "").replace(":", "")
        if "T" not in norm_obs:
            norm_obs = norm_obs[:8] + "T" + norm_obs[8:]
        if not norm_obs.endswith("Z"):
            norm_obs = norm_obs + "Z"
        if len(norm_obs) == 14:  # e.g. 20151028T1800Z
            norm_obs = norm_obs[:13] + "00Z"

        patch_path = os.path.join(
            settings.PROJECT_ROOT,
            "data",
            "processed",
            "satellite_patches",
            storm_id,
            norm_obs,
            "noaa_hursat_b1",
            channel.upper(),
            "patch.npy",
        )

        if not os.path.exists(patch_path):
            # Fallback search for matching observation folder
            storm_dir = os.path.join(settings.PROJECT_ROOT, "data", "processed", "satellite_patches", storm_id)
            if os.path.exists(storm_dir):
                target_prefix = norm_obs[:11]  # YYYYMMDDTHH
                for d in os.listdir(storm_dir):
                    if d.startswith(target_prefix):
                        cand = os.path.join(storm_dir, d, "noaa_hursat_b1", channel.upper(), "patch.npy")
                        if os.path.exists(cand):
                            patch_path = cand
                            break

        if not os.path.exists(patch_path):
            logger.warning(f"Patch file not found: {patch_path}")
            return None

        arr = np.load(patch_path)
        if arr.size == 0:
            return None

        # Handle nan values
        arr = np.nan_to_num(arr, nan=280.0)

        # Contrast enhancement for infrared thermal colormap
        # In meteorology, cold clouds (<220K) are bright/cyan, warm ocean (>285K) is dark
        if channel.upper() in ["IRWIN", "IRWVP"]:
            min_val = 185.0
            max_val = 300.0
            clipped = np.clip(arr, min_val, max_val)
            # Invert: cold is high (white/bright), warm is low (dark)
            norm = ((max_val - clipped) / (max_val - min_val) * 255.0).astype(np.uint8)
        else:
            # Visible: 0 to 1 reflectance
            min_val = np.nanmin(arr)
            max_val = np.nanmax(arr)
            if max_val > min_val:
                norm = ((arr - min_val) / (max_val - min_val) * 255.0).astype(np.uint8)
            else:
                norm = np.zeros(arr.shape, dtype=np.uint8)

        # Upscale 64x64 to 256x256 using nearest or bicubic for crisp workstation display
        img = Image.fromarray(norm, mode="L")
        img = img.resize((256, 256), resample=Image.Resampling.BILINEAR)

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
