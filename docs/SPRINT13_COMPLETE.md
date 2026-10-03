# SPRINT 13 — SCIENTIFIC EVIDENCE & HISTORICAL CASE-STUDY EXPERIENCE (FINAL REPORT)

**Project:** CycloneGuard — AI Early Warning for Rapid Tropical Cyclone Intensification  
**Team:** STORM BYTES  
**Date:** 2026-09-27  
**Status:** COMPLETE & VERIFIED  

---

## 1. Executive Summary

Sprint 13 successfully delivers an **evidence-first, scientifically rigorous historical cyclone analysis experience** for CycloneGuard. In strict adherence to scientific guidelines, **no new models were trained, no frozen weights were altered, and no synthetic satellite data was generated**.

Instead, CycloneGuard's frozen production intelligence (`CycloneGuard-RI-Multimodal-TS-Final v3.0.0-frozen`) has been made completely **traceable, understandable, visually compelling, and verifiable** across historical North Indian Ocean cyclone lifecycles.

The core user journey:
```
CYCLONE DATABASE
   ↓
HISTORICAL OBSERVATION TIMELINE
   ↓
TEMPORAL EVOLUTION & KINEMATICS
   ↓
SATELLITE STRUCTURAL EVIDENCE (NOAA HURSAT-B1)
   ↓
MODEL RI RISK INDEX (vs τ = 0.125)
   ↓
MODEL FEATURE ATTRIBUTION
   ↓
HISTORICAL 24H OUTCOME (GROUND TRUTH VERIFICATION)
```

---

## 2. Evidence Sources & Data Grounding

All displayed observations derive strictly from verified meteorological repositories:
1. **NOAA IBTrACS v04r01:** Best-track kinematic trajectory (latitude, longitude, $V_{max}$, $P_{min}$, translation speed/bearing, historical rates of change).
2. **NOAA HURSAT-B1 v06:** Geostationary infrared calibrated brightness temperatures:
   - **IRWIN (11 µm Window):** Clean infrared cloud-top temperatures ($185\text{ K} - 300\text{ K}$).
   - **IRWVP (6.7 µm Water Vapor):** Mid/upper tropospheric moisture and convective alignment.
   - **VSCHN (0.6 µm Visible):** Validated daytime reflectance; nighttime observations are honestly declared unilluminated ($0.0$).
3. **No Synthetic Imagery:** Satellite previews render the authentic $64 \times 64$ float32 patches stored on disk with exact radiometric thermal colorbars.

---

## 3. Strict Non-Negotiable Scientific Rules Compliance

| Rule | Requirement | Verification Method | Status |
| :--- | :--- | :--- | :--- |
| **Rule 1 & 2** | Do not retrain or alter frozen model | Checksums of `models/ri/final/*` verified; exact sha256 preserved. | **PASS** |
| **Rule 3 & 4** | 61-feature contract; zero environmental features | `InferenceFeatureContract` rejects any non-canonical or `env_*` variables. | **PASS** |
| **Rule 5 & 6** | No synthetic satellite imagery or fake observations | PNG generator loads real NumPy files from `satellite_patches/`. | **PASS** |
| **Rule 7** | Empirical risk index, NOT calibrated probability | Labeled "Empirical RI Risk Index" across all UI cards and charts. | **PASS** |
| **Rule 8 & 9** | Attribution labeled as model behavior, NOT physical cause | "Model Feature Attribution" with mandatory non-causality disclaimer. | **PASS** |
| **Rule 10 & 11** | Zero lookahead: Future ground truth never used as model inputs | Future fields strictly quarantined in `HistoricalOutcomeVerification`. | **PASS** |
| **Rule 12 & 13** | Clear visual separation: Observation Time ($t_0$) vs Outcome ($t_0 + 24\text{h}$) | Prominent "HISTORICAL OUTCOME — NOT USED AS MODEL INPUT" banner. | **PASS** |
| **Rule 14** | Precedence of official meteorological warnings | IMD / JTWC / RSMC warning precedence banner prominently placed. | **PASS** |

---

## 4. Architectural & Component Implementation

### 4.1 Backend Services & Endpoints
- `app.services.cyclone_seeder`: Seeds the 6 verified NIO historical cyclones (`CHAPALA`, `NILOFAR`, `PHAILIN`, `HUDHUD`, `MEGH`, `HELEN`) into SQLite.
- `app.services.case_study_service`: Encapsulates chronological timeline extraction, frozen inference execution, Section A & B assembly, and authentic satellite patch rendering.
- `GET /api/v1/cyclones`: Returns active and verified historical cyclones.
- `GET /api/v1/cyclones/historical`: Returns benchmark reanalysis metadata for the 6 historical NIO lifecycles.
- `GET /api/v1/cyclones/{storm_id}/timeline`: Returns chronological timeline items ($t_0$ coordinates, intensity, satellite flags, empirical risk index).
- `GET /api/v1/cyclones/{storm_id}/case-study`: Returns structured case study payload with strict `what_the_model_saw` vs `historical_outcome` separation.
- `GET /api/v1/cyclones/{storm_id}/observations/{obs_id}/patch/{channel}`: Renders authentic $256 \times 256$ PNG image from native $64 \times 64$ HURSAT-B1 NumPy array.

### 4.2 Frontend UI Workstation Components
- `CycloneTimeline.tsx`: Interactive horizontal observation scrubber displaying all historical fixes with coordinates, wind, satellite channel badges, and risk index badges.
- `RIRiskTimeline.tsx`: SVG time-series chart plotting Empirical RI Risk Index across the storm lifecycle with frozen operating threshold line ($\tau = 0.125$) and visual risk zones.
- `TemporalEvolutionPanel.tsx`: Displays indicators from the 23-feature kinematic set ($V_0$, $\Delta V_{6h}$, $\Delta V_{12h}$, $P_0$, $\Delta P_{6h}$, translation speed/bearing) labeled "Derived from observation history".
- `EvidencePanel.tsx`: Upgraded with authentic HURSAT-B1 infrared imagery preview, thermal colorbar scale ($185\text{ K} - 300\text{ K}$), structural proxy metrics (core $T_b$, cold cloud fraction, asymmetry), and channel status cards.
- `ModelFeatureAttributionPanel.tsx`: Displays top supporting and suppressing features with standardized contribution bars and non-causality notices.
- `PredictionOutcomeCard.tsx`: Two-stage comparative visualization with distinct Section A ("What the Model Saw" at $t_0$) and Section B ("Historical Outcome — Not Used as Model Input" at $t_0 + 24\text{h}$).
- `app/user/cyclones/[id]/case-study/page.tsx`: Full 10-section guided historical analysis workstation.
- `app/admin/predictions/page.tsx`: Updated audit inspection modal with strict separation of prediction-time inputs from historical ground truth and deep link to case study.

---

## 5. Verification Case Studies

### 5.1 Case Study 1: Cyclone CHAPALA (RI-Positive Benchmark)
- **Fix:** `2015-10-28 18:00 UTC` ($13.1^\circ\text{N}, 64.6^\circ\text{E}$)
- **Current Intensity ($V_0$):** $30\text{ kt}$
- **Empirical RI Risk Index:** **0.3592** (Well above $\tau = 0.125$)
- **Operating Category:** `HIGH_RISK`
- **Observed 24h Outcome:** $V_{24} = 65\text{ kt}$, $\Delta V_{24h} = +35\text{ kt}$
- **Ground Truth Target:** **RI+ Occurred** ($\Delta V \ge 30\text{ kt}$)
- **Evaluation:** **True Positive Detection** (High-confidence early alert).

### 5.2 Case Study 2: Cyclone NILOFAR (RI-Negative Benchmark)
- **Fix:** `2014-10-23 12:00 UTC` ($12.3^\circ\text{N}, 64.9^\circ\text{E}$)
- **Current Intensity ($V_0$):** $15\text{ kt}$
- **Empirical RI Risk Index:** **0.0002** (Well below $\tau = 0.125$)
- **Operating Category:** `LOW_RISK`
- **Observed 24h Outcome:** $V_{24} = 20\text{ kt}$, $\Delta V_{24h} = +5\text{ kt}$
- **Ground Truth Target:** **RI- (No RI)**
- **Evaluation:** **True Negative Baseline** (Zero false alarm).

### 5.3 Case Study 3: Cyclone HELEN (Pure Non-RI Lifecycle)
- **Fix:** `2013-11-18 00:00 UTC` ($13.5^\circ\text{N}, 90.0^\circ\text{E}$)
- **Current Intensity ($V_0$):** $20\text{ kt}$
- **Empirical RI Risk Index:** **0.0133** (Below $\tau = 0.125$)
- **Observed 24h Outcome:** $V_{24} = 25\text{ kt}$, $\Delta V_{24h} = +5\text{ kt}$
- **Lifecycle Context:** 43 verified observations, 0 RI+ events. Model maintained low empirical index throughout.

---

## 6. Verification & Test Results

1. **ML Unit Tests (`ml/tests/`):**
   - 112 passed, 0 failed.
   - Verified zero lookahead, real observations, frozen threshold $\tau = 0.125$, smoke test inference.
2. **Backend Integration Tests (`backend/tests/`):**
   - 109 passed, 0 failed.
   - Verified timeline, case study separation, patch image rendering, role authorization.
3. **Frontend TypeScript (`npx tsc --noEmit`):**
   - 0 errors.
4. **Frontend Production Build (`npm run build`):**
   - Compiled successfully. Static and dynamic routes generated (`/user/cyclones/[id]/case-study`).

---

## 7. Known Scientific Limitations

1. **Restricted Historical Scale:** Benchmark evaluation is conducted across 6 historical North Indian Ocean cyclone lifecycles (299 supervised samples, 39 RI+ events).
2. **Uncalibrated Empirical Score:** Model outputs represent rank-order empirical risk indices and are not calibrated Bayesian probabilities.
3. **Statistical Attribution:** Feature contributions describe linear decision boundaries and do not demonstrate physical thermodynamic causation.
4. **Authoritative Warning Precedence:** Model outputs represent research decision support. Official advisories from IMD and JTWC remain authoritative.
