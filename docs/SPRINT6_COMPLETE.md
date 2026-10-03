# Sprint 6 Final Report — Rapid Intensification Model v1

## 1. What Was Built

In **Sprint 6**, CycloneGuard developed and verified its first end-to-end **Rapid Intensification (RI) Prediction Pipeline** using exclusively verified historical outputs from Sprint 5. 

The complete architecture comprises:
* **Supervised RI Dataset Builder** ([`ml/datasets/ri_dataset.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/datasets/ri_dataset.py)) with strict forward-looking label derivation and temporal leakage assertions ($t_{\text{target}} > t_{\text{feature}}$).
* **Storm-Wise Partitioning Configuration** ([`ml/config/split_config.json`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/config/split_config.json) & [`docs/STORM_WISE_SPLIT.md`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/docs/STORM_WISE_SPLIT.md)) enforcing 100% disjoint lifecycle separation across training, validation, and testing.
* **Conventional Machine Learning Baseline** ([`ml/models/ri_baseline.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/models/ri_baseline.py)) implementing balanced regularized Logistic Regression and Random Forest with class-imbalance weighting.
* **Temporal Modeling Decision Protocol** ([`ml/models/ri_temporal.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/models/ri_temporal.py)) scientifically documenting why deep recurrent networks (LSTM/GRU) were skipped due to training set sample size ($N=227, P=18$) and environment package constraints.
* **Systematic Feature Ablation Study** ([`docs/SPRINT6_ABLATION_RESULTS.md`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/docs/SPRINT6_ABLATION_RESULTS.md)) evaluating Model A (Current State), Model B (Current + Temporal), and Model C (Current + Temporal + Multi-Source).
* **Versioned Model Package v1.0.0** ([`models/ri/v1/`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/models/ri/v1/)) containing `model.pkl`, `scaler.json`, `feature_schema.json`, and `metadata.json`.
* **Inference Engine** ([`ml/inference/ri_predictor.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/inference/ri_predictor.py)) providing deterministic inference, threshold tuning, and graceful missing-sensor handling.
* **FastAPI Service Endpoints** ([`backend/app/api/v1/endpoints/ri_models.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/backend/app/api/v1/endpoints/ri_models.py)) mounted to the main backend router.
* **User & Admin Portal Integration** ([`frontend/app/user/cyclones/[id]/page.tsx`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/frontend/app/user/cyclones/[id]/page.tsx) & [`frontend/components/ui/RIRiskPanel.tsx`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/frontend/components/ui/RIRiskPanel.tsx)) rendering real model scores, operational risk tiers, and feature attribution without synthetic placeholders.
* **Comprehensive Test Suites** ([`ml/tests/test_ri_model.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/tests/test_ri_model.py) & [`backend/tests/test_ri_endpoints.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/backend/tests/test_ri_endpoints.py)).

---

## 2. Dataset Used

* **Source Archive:** NOAA IBTrACS v04r01 North Indian Ocean 2023 season partition.
* **Storm Catalog:** 10 tropical cyclones.
* **Total Track Points:** 400 synoptic observation fixes.
* **Supervised 24h Instances:** 303 observations with valid forward $t + 24\text{h}$ verification points.
* **Total Positive RI Events:** 29 instances (prevalence: 9.57%).
* **Satellite Alignment:** NOAA HURSAT-B1 10.8 µm geostationary infraredNetCDF3 imagery (coincident for 1 fix on Mocha; absent across catalog).

---

## 3. RI Definition Implemented

Following Kaplan & DeMaria (2003) and standard WMO / National Hurricane Center (NHC) operational criteria:
$$\text{RI}_{24\text{h}} = \begin{cases} 1 & \text{if } V_{\text{max}}(t + 24\text{h}) - V_{\text{max}}(t) \ge 30\,\text{kts} \\ 0 & \text{otherwise} \end{cases}$$
* Paired within a $\pm 2.5\text{h}$ time-matching tolerance window.
* Incomplete forward tracks (e.g. cyclolysis within 24h) are assigned `None` and excluded from training.

---

## 4. Forecast Horizons Implemented

* **24-Hour Horizon ($\Delta t = 24\text{h}$):** **Trained & Evaluated.** 303 supervised samples (29 positives).
* **12-Hour Horizon ($\Delta t = 12\text{h}$):** 338 supervised samples (22 positives). Supported in dataset schema; 24h prioritized as the primary operational standard.
* **36-Hour & 48-Hour Horizons:** Insufficient continuous life-cycle duration in short-lived Bay of Bengal systems (sample count drops significantly; 48h has only 232 samples). Deferred to expanded basin datasets.

---

## 5. Models Implemented

1. **Model B — Balanced Logistic Regression (Primary Model v1):**
   * Features: 23 features (`subset_b`: Current State + Temporal Kinematic Derivatives).
   * Regularization: L2 ($C=0.1$), solver: `lbfgs`.
   * Class Balancing: `class_weight='balanced'`.
2. **Model A — Static State Baseline:**
   * Features: 13 features (`subset_a`: Current State only).
3. **Model C — Multi-Source Candidate:**
   * Features: 67 features (`subset_c`: Current State + Temporal + Multi-Source indicators/crops).
4. **Model B-RF — Balanced Random Forest (Comparative Non-Linear Baseline):**
   * Estimators: 50 trees, max depth: 4, `class_weight='balanced'`.

---

## 6. Actual Empirical Metrics (Held-Out Test Storm: Cyclone Mocha, N=43, Positives=11)

| Metric | Model A (Current State) | Model B (Current + Temporal) | Model C (Current + Temp + Multi-Source) | Model B-RF (Random Forest) |
| :--- | :---: | :---: | :---: | :---: |
| **ROC-AUC** | 0.6023 | **0.6619** | **0.6619** | 0.6719 |
| **PR-AUC** | 0.3005 | **0.3372** | **0.3372** | 0.4001 |
| **F1 Score** | 0.5128 | **0.5405** | **0.5405** | 0.4074 |
| **Recall (Sensitivity)** | 90.91% | **90.91%** | **90.91%** | 100.0% |
| **Precision** | 35.71% | **38.46%** | **38.46%** | 25.58% |
| **Accuracy** | 58.14% | **60.47%** | **60.47%** | 25.58% |
| **Brier Score** | 0.2433 | **0.2311** | **0.2310** | 0.2647 |
| **Confusion Matrix** | TN: 15, FP: 17<br>FN: 1, TP: 10 | **TN: 16, FP: 16<br>FN: 1, TP: 10** | **TN: 16, FP: 16<br>FN: 1, TP: 10** | TN: 0, FP: 32<br>FN: 0, TP: 11 |

*Note: While Random Forest achieved higher PR-AUC, it suffered total specificity collapse (TN=0, predicting every point as positive). Logistic Regression provided balanced operational utility.*

---

## 7. Ablation Results

* **Temporal Evolution Impact:** Adding temporal rate-of-change derivatives ($\Delta V_{6h}, \Delta V_{12h}, \Delta P_{6h}, dV/dt$) yielded:
  * $+9.9\%$ gain in ROC-AUC ($0.6023 \rightarrow 0.6619$).
  * $+12.2\%$ gain in PR-AUC ($0.3005 \rightarrow 0.3372$).
  * $+5.4\%$ gain in F1 score ($0.5128 \rightarrow 0.5405$), reducing False Positives from 17 to 16 while preserving 90.9% recall.
* **Multi-Source Evidence Impact:** Because infrared coverage is sparse (1 coincident fix) and microwave is unobserved in the historical sample, Model C achieved exact parity with Model B. Sensor indicators were correctly set to absent.

---

## 8. Probability Calibration Status

* **Status:** **Uncalibrated Model Score.**
* **Scientific Rationale:** The 2 validation storms contained 0 positive RI events at the 24h horizon with strict time-matching. Fitting Platt scaling or isotonic regression on a 0%-positive validation split is mathematically degenerative.
* **Interface Handling:** Outputs are clearly labeled "Model RI score: X" and "Uncalibrated Model Score".

---

## 9. Model Version & Artifacts

* **Package:** `models/ri/v1/`
* **Version:** `v1.0.0`
* **Model File:** `model.pkl` (Balanced Logistic Regression)
* **Scaler:** `scaler.json` (Fitted strictly on 227 training observations)
* **Feature Schema:** `feature_schema.json` (23 features)
* **Metadata:** `metadata.json` (Complete split hashes and training provenance)

---

## 10. API Endpoints Mounted & Verified

* `GET /api/v1/models/ri`: Model metadata, architecture, threshold, and metrics.
* `POST /api/v1/predictions/ri`: Real-time prediction from raw observation payload.
* `GET /api/v1/cyclones/{storm_id}/ri-risk`: Look up real RI prediction on verified storm track.
* `GET /api/v1/predictions/ri/{storm_id}`: Prediction alias matching REST standards.
* `GET /api/v1/admin/models/ri`: Dedicated administrative artifact inspection (requires ADMIN role).

---

## 11. UI Integration

* **User Portal Cyclone Detail Page** ([`frontend/app/user/cyclones/[id]/page.tsx`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/frontend/app/user/cyclones/[id]/page.tsx)):
  * Automatically requests `/api/v1/cyclones/{id}/ri-risk`.
  * Displays "Evaluated (Sprint 6 Model v1)" status badge.
  * Shows "Elevated RI Risk" (warning) vs "Low RI Risk" (success).
  * Shows uncalibrated Model RI Score (`0.000` to `1.000`).
  * Shows Decision Threshold ($\theta = 0.02$ or $0.05$).
  * Shows Observational Evidence, Data Quality flags, and Documented Limitations.
* **Admin Portal** ([`frontend/app/admin/models/page.tsx`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/frontend/app/admin/models/page.tsx)):
  * Connected to `/api/v1/admin/models` and `/api/v1/admin/models/ri`.
  * Truthfully displays `ri_model_v1` metadata alongside deep learning research placeholders.

---

## 12. Explainability

* Integrated linear feature attribution:
  $$\text{Attribution}_j = w_j \cdot \tilde{x}_j$$
* Displays Top Supporting Features (e.g. `prev_intensity_change_6h`, `wind_speed_kts`) and Top Suppressing Features (e.g. `pressure_drop_rate_mb_per_hour`).
* Explicit disclaimer displayed: *"Statistical model weights within the linear model; does not establish physical causation."*

---

## 13. Limitations Documented

Stored in [`docs/SPRINT6_LIMITATIONS.md`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/docs/SPRINT6_LIMITATIONS.md):
1. Small sample size ($N=303$ supervised, 29 positives).
2. Validation partition had 0 positive events.
3. Satellite IR and microwave sensors are sparse in current sample partition.
4. North Indian Ocean exclusivity (unverified in other basins).
5. Ground truth based on subjective Dvorak estimates.
6. Not an operational deployment; IMD advisories have legal primacy.

---

## 14. Test Suite Execution

* **Backend Tests:** **77 passed out of 77** (`pytest backend/tests/ -v`).
* **ML Tests:** **42 passed out of 42** (`pytest ml/tests/ -v`).
* **Frontend TypeScript & Build:** **Clean build (`0 errors, 20 routes static/dynamic`)**.

---

## 15. Known Issues

* **Validation Partition Imbalance:** Future dataset expansion must balance positive RI events across validation splits so Platt scaling can be fitted.
* **HURSAT IR Data Alignment:** Expanding coincident HURSAT files beyond the single test crop to train spatial CNN features.

---

## 16. Recommended Next Sprint

* **Sprint 7 Objective:** Multi-Basin Dataset Expansion & Spatial Vision Integration.
  * Ingest 2018–2024 North Indian Ocean and Western North Pacific historical tracks to expand sample size to $>2,000$ supervised instances.
  * Ingest coincident INSAT-3D and HURSAT imagery to unlock computer vision feature extraction for Model C.
