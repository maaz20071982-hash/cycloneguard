# CycloneGuard Sprint 11 — Audit of Existing Model Artifacts & Baseline Architecture

**Date:** September 2026  
**Author:** AI Systems Lead (STORM BYTES Pair Programmer)  
**Deliverable:** Phase 1 Audit for Sprint 11 Final Multi-Storm Validation & Model Freeze

---

## 1. Executive Summary

Sprint 10 concluded the data-validation and multimodal investigation for CycloneGuard:
- Real oceanic (NOAA OISST v2.0 Daily High-Res) and atmospheric (NOAA PSL NCEP/DOE Reanalysis 2 6-hourly) environmental data were matched to all 347 historical observations under strict causal constraints ($t_{\text{env}} \le t_{\text{obs}}$, temporal offset $\le 150$ min).
- The empirical evaluation on held-out test storm **CHAPALA** yielded **CLASSIFICATION B** (*"Environmental variables available but no measurable incremental signal demonstrated"*):
  - Model T (Temporal, 23 features): ROC-AUC = 0.8279, PR-AUC = 0.4011
  - Model TS (Temporal + Spatial, 61 features): ROC-AUC = 0.7349, PR-AUC = 0.6109
  - Model E (Environmental, 13 features): ROC-AUC = 0.3581, PR-AUC = 0.1582
  - Model STE (Full Multimodal, 74 features): ROC-AUC = 0.5070, PR-AUC = 0.2333
- Consequently, environmental features are strictly excluded from the finalist production models in Sprint 11.
- Sprint 11 focuses exclusively on the two finalist architectures:
  1. **Finalist T (Temporal Kinematic Baseline, 23 features)**
  2. **Finalist TS (Temporal + Satellite Spatial Structure, 61 features)**

The central research question is whether these models remain scientifically defensible across multiple unseen cyclone lifecycles, or whether their performance is an artifact of the single test storm Chapala.

---

## 2. Dataset State & Storm Cohort Audit

The verified historical dataset comprises 6 North Indian Ocean cyclones with 347 coincident track and HURSAT-B1 infrared/water-vapor observations, yielding **299 supervised 24-hour Rapid Intensification (RI) samples** ($V_{t+24\text{h}} - V_t \ge 30\text{ kts}$):

| Storm Name | Season / Basin | Total Fixes | Valid Supervised RI Fixes | RI+ Count | RI- Count | Prevalence | Role in Sprint 8–10 Partition |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **PHAILIN** | 2013 / BoB | 55 | 45 | 11 | 34 | 24.4% | TRAIN |
| **HELEN** | 2013 / BoB | 43 | 36 | 0 | 36 | 0.0% | TRAIN (Null RI Cohort) |
| **HUDHUD** | 2014 / BoB | 66 | 57 | 1 | 56 | 1.8% | TRAIN (Low RI Cohort) |
| **NILOFAR** | 2014 / AS | 73 | 66 | 11 | 55 | 16.7% | TRAIN |
| **MEGH** | 2015 / AS | 49 | 42 | 6 | 36 | 14.3% | VAL (Threshold Tuning) |
| **CHAPALA** | 2015 / AS | 61 | 53 | 10 | 43 | 18.9% | TEST (Held-Out Final Evaluation) |
| **TOTAL** | — | **347** | **299** | **39** | **260** | **13.04%** | — |

### Key Observation on Class Diversity
- **Helen** contains **0 RI+ events** (all 36 supervised fixes are RI-negative). In leave-one-storm-out validation where Helen is the evaluation target, ROC-AUC and PR-AUC are mathematically undefined ($N_{\text{pos}} = 0$). Accuracy, false alarm rate, and Brier score remain fully computable.
- **Hudhud** contains only **1 RI+ event** (prevalence 1.8%). Metrics will exhibit high discretization sensitivity.
- **Phailin**, **Nilofar**, **Megh**, and **Chapala** exhibit representative RI prevalence ($14.3\% - 24.4\%$).

---

## 3. Existing Model Artifacts & Feature Definitions

### 3.1 Finalist T — Temporal Kinematics (23 Features)
- **Source Module:** [`ml/datasets/spatial_ri_dataset.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/datasets/spatial_ri_dataset.py) (`TEMPORAL_FEATURE_NAMES`)
- **Features:**
  1. `track_latitude_val`, `track_latitude_is_observed`
  2. `track_longitude_val`, `track_longitude_is_observed`
  3. `track_wind_speed_val`, `track_wind_speed_is_observed`
  4. `track_pressure_val`, `track_pressure_is_observed`
  5. `track_translation_speed_kts_val`, `track_translation_speed_kts_is_observed`
  6. `track_translation_bearing_deg_val`, `track_translation_bearing_deg_is_observed`
  7. `temp_delta_wind_6h_val`, `temp_delta_wind_6h_is_observed`
  8. `temp_delta_wind_12h_val`, `temp_delta_wind_12h_is_observed`
  9. `temp_delta_pressure_6h_val`, `temp_delta_pressure_6h_is_observed`
  10. `temp_wind_change_rate_per_hour_val`, `temp_wind_change_rate_per_hour_is_observed`
  11. `temp_delta_ir_min_6h_val`, `temp_delta_ir_min_6h_is_observed`
  12. `quality_track_available`

### 3.2 Finalist TS — Temporal Kinematics + Satellite Spatial Proxies (61 Features)
- **Source Module:** [`ml/datasets/spatial_ri_dataset.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/datasets/spatial_ri_dataset.py) (`MODEL_TS_FEATURES`)
- **Features:** 23 Temporal Features + 38 Physical HURSAT-B1 Spatial Features:
  - **Family A: Bulk IR Statistics (12):** Mean, std, min, p10, p25, p50, p75, max, temp range, cold fraction (< 233K), very cold fraction (< 219K), overshooting top fraction (< 203K).
  - **Family B: Radial Core/Ring Structure (11):** Core mean, core min, core cold fraction, core very cold fraction, ring mean, ring min, ring cold fraction, outer mean, core-ring difference, core-outer difference, core azimuthal standard deviation.
  - **Family C: Texture & Gradients (4):** Mean spatial gradient, max gradient, local variance, spatial entropy.
  - **Family D: Multispectral IR/WV Channels (7):** Channel availability flag, WV mean, WV min, WV core mean, IR-WV mean difference, IR-WV core difference, IR-WV spatial correlation.
  - **Family E: Visible Channel (4):** Channel availability flag, visible mean, visible core mean, visible standard deviation.

---

## 4. Preprocessing & Leakage Safeguards Audit

The baseline preprocessing protocol adheres to strict scientific safeguards:
1. **Storm-Wise Isolation:** Samples are grouped strictly by cyclone lifecycle. Individual observations from the same storm never appear in both training and evaluation folds.
2. **Train-Only Preprocessing:**
   - **Imputer:** `SimpleImputer(strategy="median")` fitted strictly on training storm data and applied without refitting to validation/test storms.
   - **Scaler:** `StandardScaler()` fitted strictly on training storm data and applied without refitting.
3. **Threshold Selection:**
   - Decision threshold is selected by evaluating a grid of thresholds (0.05 to 0.95) on the out-of-fold validation storm to maximize F1 score.
   - Test storm data is **never** observed during scaler fitting, imputer fitting, model coefficient optimization, or threshold selection.
4. **Causality & Horizon:**
   - All temporal features observe strictly contemporaneous or historical intervals ($t \le t_0$, $\Delta t \in [-12\text{h}, 0]$).
   - Ground truth target represents $V_{t+24\text{h}} - V_t \ge 30\text{ kts}$.
   - No future observations enter feature construction.

---

## 5. Potential Blockers & Investigation Plan for Sprint 11

1. **Leave-One-Storm-Out (LOSO) Implementation:**
   - With 6 storms, holding out 1 storm leaves 5 storms.
   - To strictly follow the protocol where the decision threshold is determined before evaluating the test storm:
     - For each evaluation storm $S_{\text{test}} \in \{\text{Phailin}, \text{Helen}, \text{Hudhud}, \text{Nilofar}, \text{Megh}, \text{Chapala}\}$:
     - The remaining 5 storms are partitioned into 4 training storms and 1 validation storm (or an internal 4-fold cross-validation across the 5 training storms to select the operating threshold).
     - Then, the model is evaluated exactly once on $S_{\text{test}}$.
2. **Handling Zero-Prevalence Storms:**
   - Storm Helen has 0 RI+ samples. ROC-AUC and PR-AUC cannot be calculated. The framework must return `None` or an explicit indicator `"Undefined — insufficient class diversity"` rather than imputing 0.0 or failing.
3. **Calibration Reliability:**
   - With only 39 total RI+ events across the entire dataset, Platt scaling or isotonic regression on small validation cohorts ($N=42$ or $N=53$) is known to be noisy and prone to overfitting. Calibration status must be assessed empirically with Brier scores and reliability diagrams, but not overclaimed.
4. **Feature Stability:**
   - Logistic regression coefficients must be tracked across all storm folds to determine whether the top features (e.g., core cold cloud fraction, $\Delta V_{6\text{h}}$, pressure) maintain consistent sign and rank across different cyclone lifecycles.
