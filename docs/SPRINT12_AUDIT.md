# CycloneGuard Sprint 12 Audit: Inference Pipeline & Production Architecture

**Project:** CycloneGuard — AI Early Warning for Rapid Tropical Cyclone Intensification  
**Team:** STORM BYTES  
**Date:** September 2026  
**Status:** Phase 1 Complete — Inference Pipeline & Integration Audit  

---

## 1. Executive Summary

Sprint 11 finalized and froze the production model **`CycloneGuard-RI-Multimodal-TS-Final`** (`v3.0.0-frozen`). Sprint 12 bridges the scientific frozen artifacts with the live full-stack application (FastAPI backend + Next.js frontend). This audit documents the current inference paths, API endpoints, feature preparation mechanisms, database models, frontend presentation components, and authorization boundaries, establishing the implementation gap for Sprint 12.

---

## 2. Model Loading Behavior & Artifact Integrity

### 2.1 Frozen Model Artifacts
The frozen production artifacts reside in `models/ri/final/`:
- `model.pkl`: Regularized Balanced Logistic Regression (L2 penalty, C=1.0, solver=lbfgs).
- `scaler.pkl`: `StandardScaler` fitted strictly on training cohorts (Phailin, Helen, Hudhud, Nilofar; N=204).
- `imputer.pkl`: `SimpleImputer` (median) fitted strictly on training cohorts.
- `feature_schema.json`: Schema defining 61 canonical feature names (23 temporal, 38 spatial).
- `model_manifest.json`: Full immutable metadata, operating threshold ($\tau = 0.125$), LOSO metrics, provenance, and limitations.

### 2.2 Model Loader Audit
- `ml/inference/frozen_model.py`: Implements `FrozenModelLoader`.
  - Enforces loading exclusively from `models/ri/final/`.
  - Verifies manifest presence and model version `v3.0.0-frozen`.
  - Validates exact 61 features and their ordering.
  - Computes standardized linear feature attributions ($w_i \cdot x_{\text{scaled}, i}$).
  - Strictly prevents fallback to historical `v1` or `v2` models.
- **Audit Finding:** The loader is structurally sound but was not yet integrated into the backend service layer (`backend/app/services/prediction/`).

---

## 3. Current Inference Path vs. Frozen Model

### 3.1 Existing Inference Implementations
1. **`ml/inference/ri_predictor.py` (Sprint 6 legacy):**
   - Loads `models/ri/v1/` or `models/baseline/v1/`.
   - Relies on older 23-feature or 69-feature state encoder.
   - Operating threshold $\tau = 0.05$.
   - **Status:** Deprecated for production prediction. Must be superseded by the frozen v3.0.0 loader.
2. **`backend/app/api/v1/endpoints/ri_models.py`:**
   - Mounts `/api/v1/predictions/ri` and `/api/v1/cyclones/{storm_id}/ri-risk`.
   - Calls `RIPredictor.load_default()` (Sprint 6 legacy).
   - Does not enforce the 61-feature multimodal contract or HURSAT spatial feature inputs.
3. **`backend/app/api/v1/endpoints/analysis.py`:**
   - Mounts `/api/v1/analysis/cyclone`.
   - Uses `models/baseline/v1/` (Sprint 5 offline baseline).

---

## 4. Feature Contract & Preparation Behavior

### 4.1 61-Feature Multimodal Schema
The production schema requires:
- **23 Temporal Kinematic Features:** Track position, intensity, central pressure, translation velocity/bearing, 6h/12h wind/pressure tendencies, change rates, and observational quality flags.
- **38 HURSAT Spatial Structural Features:** Bulk IR brightness temperature statistics, radial core/ring metrics, texture/entropy gradients, IR/WV multispectral metrics, and visible channel metrics.

### 4.2 Strict Constraints
- **Environmental Features Excluded:** Any feature with prefix `env_` must be immediately rejected with `FeatureContractViolationError`.
- **Explicit Missingness:** No silent substitution of unobserved features with zeros. Missing channels use explicit indicators (`has_irwvp=0.0`, `has_vschn=0.0`, `*_is_observed=0.0`) and median imputation for unobserved physical values.
- `ml/inference/feature_contract.py` defines `InferenceFeatureContract` and implements these rules.

---

## 5. Backend Service & API Layer Audit

### 5.1 Missing Service Layer
- `backend/app/services/prediction/` did not exist.
- Inference was called directly within FastAPI endpoint handlers, violating service boundary architecture.

### 5.2 Persistence & Database Audit
- `backend/app/models/prediction.py` defines `Prediction` with fields for `ri_risk_index`, `operating_threshold`, `ri_flag`, `risk_category`, `input_provenance`, etc.
- In `cycloneguard.db`, the existing `predictions` table only contained legacy columns (`estimated_vmax_knots`, `ri_probability_24h`).
- **Gap:** Database schema migration is required to align table columns with the ORM model.

### 5.3 Audit Trail Audit
- Prediction execution was not being logged to `audit_logs` table.
- Prediction creation events must be recorded with user identity, storm ID, model version, and success status.

---

## 6. Frontend Portal Audit

### 6.1 User Portal (`/user/dashboard`, `/user/monitor`, `/user/cyclones/[id]`)
- `/user/cyclones/[id]/page.tsx`:
  - Displays "Sprint 6 Rapid Intensification Model v1 Active".
  - Calls `getCycloneRIRisk` which returns legacy v1 fields.
  - Contains references to "Model B" and outdated threshold $\tau=0.05$.
- `RIRiskPanel.tsx`:
  - Contains fallback tiers like "Low Risk (< 20%)" and displays atmospheric shear / SST boundary condition slots.
- `EvidencePanel.tsx`:
  - Contains environmental reanalysis slots (Sprint 10) which must be replaced or clearly disconnected from production prediction.
  - Needs honest display when satellite imagery/structure is absent.

### 6.2 Admin Portal (`/admin/models`, `/admin/predictions`)
- `/admin/models`:
  - Already displays `finalFrozenModel` from `/api/v1/admin/models/final`.
  - Shows legacy experimental baselines (S, ST, E, STE) correctly.
- `/admin/predictions`:
  - Currently displays a static empty state stating "Awaiting model deployment in Sprint 4".
  - Needs connection to real prediction records queryable from the database with storm, category, and date filtering.

---

## 7. Authorization & Security Boundaries

| Endpoint | Target Role | Current Status | Required Action |
| :--- | :--- | :--- | :--- |
| `POST /api/v1/predictions/ri` | `USER` or `ADMIN` | Requires JWT | Update to call `PredictionService` with frozen model |
| `GET /api/v1/predictions/ri/{id}` | `USER` or `ADMIN` | Not implemented | Implement with owner/admin record access |
| `GET /api/v1/predictions/ri/storm/{storm_id}` | `USER` or `ADMIN` | Implemented with v1 | Update to return verified frozen predictions |
| `GET /api/v1/admin/predictions` | `ADMIN` only | Returns static mock | Connect to `Prediction` ORM with filters |
| `GET /api/v1/admin/models/*` | `ADMIN` only | Enforced with `require_admin` | Verified secure |

---

## 8. Summary of Action Items for SPRINT 12

1. **Loader:** Ensure `ml/inference/frozen_model.py` and `ml/inference/feature_contract.py` are production-hardened.
2. **Service:** Build `backend/app/services/prediction/service.py` (`PredictionService`) adhering to strict service boundaries.
3. **Database:** Update SQLite database schema to support all `Prediction` model columns.
4. **API:** Upgrade `/api/v1/predictions/ri` endpoints and add `GET /api/v1/predictions/ri/{prediction_id}`.
5. **Audit:** Add audit logging for prediction invocations.
6. **Frontend:** Update `RIRiskPanel.tsx`, `EvidencePanel.tsx`, `/user/cyclones/[id]/page.tsx`, and `/admin/predictions/page.tsx`.
7. **Verification:** Add comprehensive ML and backend tests, verify end-to-end historical prediction flow on verified Chapala observation, and verify zero fake live data.
