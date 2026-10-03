# SPRINT 12 — PRODUCTION PREDICTION INTEGRATION ARCHITECTURE

**Project:** CycloneGuard — AI Early Warning for Rapid Tropical Cyclone Intensification  
**Team:** STORM BYTES  
**Date:** 2026-09-27  
**Model:** `CycloneGuard-RI-Multimodal-TS-Final` (`v3.0.0-frozen`)  
**Status:** Certified Production Integration  

---

## 1. High-Level Architecture Overview

Sprint 12 transitions CycloneGuard from scientific model freeze (Sprint 11) to a fully connected, auditable, and end-to-end production early warning system. The frozen scientific model artifact (`v3.0.0-frozen`) is integrated into a unified service boundary without retraining, modification of weights, or feature schema drift.

```
+-----------------------------------------------------------------------------------+
|                        VERIFIED OBSERVATIONAL STREAMS                             |
|  - NOAA IBTrACS v04r01 (Best-Track Kinematics, 23 Features)                       |
|  - NOAA HURSAT-B1 v06 (Geostationary 3-hourly IR & WV NetCDF, 38 Features)        |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|                    INFERENCE FEATURE CONTRACT (Strict 61-Feats)                   |
|  - ml/inference/feature_contract.py                                               |
|  - Exact 61-feature canonical sequence matching models/ri/final/feature_schema.json|
|  - Strict environmental firewall: Rejects all 'env_*' features                    |
|  - Explicit missingness tracking (has_irwvp, has_vschn; NEVER silent zero-fill)   |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|                      FROZEN MODEL LOADER & RUNNER                                 |
|  - ml/inference/frozen_model.py                                                   |
|  - Loads strictly from models/ri/final/ (model.pkl, scaler.pkl, imputer.pkl)      |
|  - Regularized Balanced Logistic Regression (L2, C=1.0, lbfgs)                    |
|  - Imputation via Train-fitted Median Imputer; Standardized via Train Scaler     |
|  - Evaluates empirical score vs. operating decision threshold (tau = 0.125)       |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|                           PREDICTION SERVICE BOUNDARY                             |
|  - backend/app/services/prediction/service.py                                     |
|  - Orchestrates observation lookup, contract validation, and inference           |
|  - Assigns Risk Presentation Categories (LOW_RISK, ELEVATED_RISK, HIGH_RISK)      |
|  - Assembles cryptographic provenance & attribution metrics                       |
|  - Persists to Database (predictions table) & Logs to audit_logs                  |
+-----------------------------------------------------------------------------------+
                   │                                             │
                   ▼                                             ▼
+------------------------------------+        +-------------------------------------+
|        USER PORTAL EXPERIENCE      |        |        ADMIN MONITORING & AUDIT     |
|  - /user/cyclones/[id]             |        |  - /admin/predictions               |
|  - RIRiskPanel (Index, Tau, Tier)  |        |  - /admin/models                    |
|  - EvidencePanel (HURSAT + Track)  |        |  - Query filters (Storm, Category)  |
|  - Mandatory Authoritative Advisory|        |  - Forensic Inspect Modal           |
+------------------------------------+        +-------------------------------------+
```

---

## 2. Request Flow & Service Lifecycle

1. **Submission / Query:**
   - A client initiates a prediction request via `POST /api/v1/predictions/ri` or queries an existing storm via `GET /api/v1/cyclones/{storm_id}/ri-risk`.
   - The API enforces JWT authentication (`get_current_active_user`).
2. **Feature Gathering & Contract Assembly:**
   - `PredictionService` inspects the request. If explicit feature vectors are passed, they are validated against `InferenceFeatureContract`.
   - If kinematic coordinates and winds are provided without spatial features, satellite channels are marked unobserved (`has_irwvp=0.0`, `has_vschn=0.0`, `irwin_* = np.nan`) and processed through the train-fitted median imputer.
   - If the observation matches historical catalog records (e.g. Cyclone Chapala, Phailin, etc.), coincident verified HURSAT-B1 spatial structural features are loaded.
3. **Inference Execution:**
   - `FrozenModelLoader` executes:
     $$\mathbf{x}_{\text{imputed}} = \text{SimpleImputer}(\mathbf{x}_{\text{raw}})$$
     $$\mathbf{x}_{\text{scaled}} = \text{StandardScaler}(\mathbf{x}_{\text{imputed}})$$
     $$s_{\text{RI}} = \sigma(\mathbf{w}^T \mathbf{x}_{\text{scaled}} + b)$$
4. **Classification & Risk Mapping:**
   - If $s_{\text{RI}} < 0.125$: `LOW_RISK`
   - If $0.125 \le s_{\text{RI}} < 0.350$: `ELEVATED_RISK`
   - If $s_{\text{RI}} \ge 0.350$: `HIGH_RISK`
   - Operational Decision Flag: $\text{RI Flag} = (s_{\text{RI}} \ge 0.125)$
5. **Persistence & Auditing:**
   - The prediction record is persisted in SQLite/PostgreSQL `predictions` table with cryptographic UUID.
   - An event with action `GENERATE_PREDICTION` is written to `audit_logs`.
6. **Structured Response:**
   - Returns validated `PredictionResponse` Pydantic schema with complete traceability, feature attributions, and disclaimers.

---

## 3. Strict Feature Contract

The 61-feature contract is immutable and defined in `ml/inference/feature_contract.py`:
- **Temporal Kinematic Features (23):**
  - Track Position & Intensity: `track_latitude_val`, `track_latitude_is_observed`, `track_longitude_val`, `track_longitude_is_observed`, `track_wind_speed_val`, `track_wind_speed_is_observed`, `track_pressure_val`, `track_pressure_is_observed`
  - Motion Kinematics: `track_translation_speed_kts_val`, `track_translation_speed_kts_is_observed`, `track_translation_bearing_deg_val`, `track_translation_bearing_deg_is_observed`
  - Temporal Rate-of-Change: `temp_delta_wind_6h_val`, `temp_delta_wind_6h_is_observed`, `temp_delta_wind_12h_val`, `temp_delta_wind_12h_is_observed`, `temp_delta_pressure_6h_val`, `temp_delta_pressure_6h_is_observed`, `temp_wind_change_rate_per_hour_val`, `temp_wind_change_rate_per_hour_is_observed`, `temp_delta_ir_min_6h_val`, `temp_delta_ir_min_6h_is_observed`
  - Track Quality Flag: `quality_track_available`
- **Satellite Spatial Structural Features (38):**
  - Bulk IR Statistics (Family A, 12): `irwin_mean`, `irwin_std`, `irwin_min`, `irwin_p10`, `irwin_p25`, `irwin_p50`, `irwin_p75`, `irwin_max`, `irwin_temp_range`, `irwin_cold_cloud_fraction_233k`, `irwin_very_cold_cloud_fraction_219k`, `irwin_overshooting_fraction_203k`
  - Core & Ring Structural Proxies (Family B, 11): `irwin_core_mean`, `irwin_core_min`, `irwin_core_cold_frac`, `irwin_core_very_cold_frac`, `irwin_ring_mean`, `irwin_ring_min`, `irwin_ring_cold_frac`, `irwin_outer_mean`, `irwin_core_ring_diff`, `irwin_core_outer_diff`, `irwin_azimuthal_std_core`
  - Spatial Texture & Gradients (Family C, 4): `irwin_grad_mean`, `irwin_grad_max`, `irwin_local_variance`, `irwin_spatial_entropy`
  - Water Vapor Structure (Family D, 7): `has_irwvp`, `irwvp_mean`, `irwvp_min`, `irwvp_core_mean`, `ir_wv_diff_mean`, `ir_wv_core_diff`, `ir_wv_spatial_corr`
  - Visible Albedo Proxies (Family E, 4): `has_vschn`, `vschn_mean`, `vschn_core_mean`, `vschn_std`

### Environmental Exclusion Rule
Per Sprint 10 scientific ablation, large-scale atmospheric reanalysis variables (`env_vertical_wind_shear_kts`, `env_sea_surface_temp_celsius`, `env_relative_humidity_700hpa_pct`) diluted predictive precision and caused over-prediction. Submitting any key starting with `env_` triggers an immediate `EnvironmentalFeatureForbiddenError` (HTTP 400).

---

## 4. Database Schema & Migration

Database migration `c3d4e5f6a7b8_update_predictions_table_sprint12.py` adds full prediction traceability to the `predictions` table:
- `storm_id` (VARCHAR(50)): Storm identifier
- `storm_name` (VARCHAR(100)): Storm designation
- `observation_time` (DATETIME): Timestamp of observation fix
- `prediction_time` (DATETIME): Timestamp of inference
- `model_name` (VARCHAR(100)): Certified model name
- `model_version` (VARCHAR(50)): `v3.0.0-frozen`
- `ri_risk_index` (FLOAT): Empirical score $s_{\text{RI}} \in [0, 1]$
- `operating_threshold` (FLOAT): Operating decision cutoff ($\tau = 0.125$)
- `ri_flag` (BOOLEAN): Decision classification
- `risk_category` (VARCHAR(30)): Presentation category
- `forecast_horizon_hours` (FLOAT): 24.0 hours
- `temporal_evidence_available` (BOOLEAN): Flag
- `satellite_evidence_available` (BOOLEAN): Flag
- `satellite_channels` (JSON): Array of observed spectral channels
- `input_provenance` (JSON): Provenance dictionary
- `explanation_metadata` (JSON): Supporting and suppressing feature attributions
- `requested_by` (VARCHAR(100)): User identifier/email

---

## 5. Security & Role Authorization

- **User Access:**
  - Authenticated standard users (`USER` role) can submit observations to `POST /api/v1/predictions/ri`.
  - Can inspect predictions and storm-level risk indices via `GET /api/v1/cyclones/{storm_id}/ri-risk`.
  - Can retrieve specific stored predictions via `GET /api/v1/predictions/ri/{id}`.
- **Admin Access:**
  - Requires `ADMIN` role (`require_admin` dependency).
  - Can monitor all predictions across all users via `GET /api/v1/admin/predictions`.
  - Can filter by storm name/ID, model version, risk category, and date.
  - Can inspect full forensic audit details via `GET /api/v1/admin/predictions/{id}`.
  - Standard users attempting to query admin prediction routes receive `403 Forbidden`.
- **Integrity Safeguards:**
  - Raw filesystem paths, model weight bytes, and user passwords are never exposed in responses or logs.

---

## 6. Documented Operational Limitations

1. **Dataset Scale:** Evaluated across 6 unique historical North Indian Ocean cyclone lifecycles (299 supervised samples, 39 RI+ events).
2. **Scientific Classification C:** Multi-storm cross-validation evidence is promising, but the sample scale remains insufficient for autonomous operational warning claims.
3. **Uncalibrated Empirical Score:** Platt scaling and isotonic regression could not be validated without over-fitting; outputs must be presented as empirical risk indices, not guaranteed probabilities.
4. **Authoritative Warning Precedence:** Official forecasts, track cones, and warnings issued by national authorities (India Meteorological Department — IMD, Joint Typhoon Warning Center — JTWC) remain authoritative. CycloneGuard serves strictly as research decision support.
