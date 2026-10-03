# SPRINT 13 — EVIDENCE AUDIT & PROVENANCE SPECIFICATION

**Project:** CycloneGuard — AI Early Warning for Rapid Tropical Cyclone Intensification  
**Team:** STORM BYTES  
**Date:** 2026-09-27  
**Status:** COMPLETE (Phase 1 Deliverable)  

---

## 1. Overview & Audit Objectives

The purpose of this audit is to catalogue all verified historical evidence data assets, establish strict temporal boundaries between **prediction-time observations** and **post-observation outcomes**, and specify exact presentation rules for the Sprint 13 interactive case-study experience.

In strict adherence to Non-Negotiable Scientific Rules 10–13:
- Historical future observations may be shown **ONLY as outcome / ground-truth context**.
- Historical future observations **MUST NEVER be presented as inputs used by the model at prediction time**.
- The system must explicitly and visually separate **OBSERVATION TIME** from **OUTCOME / VERIFICATION TIME**.
- The model feature attributions must describe **statistical model weights**, not physical causation.

---

## 2. Available Historical Observation Cohort

Data Assets Inspected:
- `data/processed/hursat_ri_samples.csv` (347 coincident observations across 6 North Indian Ocean cyclones)
- `data/processed/satellite_patches/` (61 observation patches for Chapala, plus Phailin, Helen, Hudhud, Nilofar, Megh)
- `data/manifests/satellite_manifest.jsonl`
- `data/reports/sprint11_error_analysis.csv`

### Storm-by-Storm Breakdown:
| Storm Name | WMO Basin / Region | Total Coincident Fixes | Supervised Samples (24h Track Valid) | RI+ Events ($\Delta V \ge 30$ kt) | Partition (Sprint 11 Protocol) |
|:---|:---|:---:|:---:|:---:|:---:|
| **PHAILIN (2013)** | Bay of Bengal | 55 | 45 | 11 | Train |
| **HELEN (2013)** | Bay of Bengal | 43 | 36 | 0 | Train |
| **HUDHUD (2014)** | Bay of Bengal | 66 | 57 | 1 | Train |
| **NILOFAR (2014)** | Arabian Sea | 73 | 66 | 11 | Train |
| **MEGH (2015)** | Arabian Sea | 49 | 42 | 6 | Validation ($\tau$-tuning) |
| **CHAPALA (2015)** | Arabian Sea | 61 | 53 | 10 | Held-Out Test Benchmark |
| **TOTAL** | **NIO** | **347** | **299** | **39** | **Multi-Storm Certified** |

---

## 3. Evidence Feature Taxonomy & Temporal Firewalls

### Category A: INFERENCE-TIME OBSERVATIONAL EVIDENCE ($t \le t_{\text{obs}}$)
*Safe to present to the user and feed into Frozen Model v3.0.0-frozen.*

#### 1. Temporal Track Kinematics (23 Features)
- **Source:** NOAA IBTrACS v04r01 (WMO verified track points)
- **Temporal Constraint:** Derived exclusively from historical observations at or prior to $t_{\text{obs}}$ ($t_0, t_{-6\text{h}}, t_{-12\text{h}}, t_{-24\text{h}}$).
- **Available Variables:**
  - `track_latitude_val`, `track_latitude_is_observed`
  - `track_longitude_val`, `track_longitude_is_observed`
  - `track_wind_speed_val`, `track_wind_speed_is_observed` (Current 10-min sustained Vmax)
  - `track_pressure_val`, `track_pressure_is_observed` (Central MSLP in hPa)
  - `track_translation_speed_kts_val`, `track_translation_speed_kts_is_observed`
  - `track_translation_bearing_deg_val`, `track_translation_bearing_deg_is_observed`
  - `temp_delta_wind_6h_val`, `temp_delta_wind_6h_is_observed` ($\Delta V_{6\text{h}}$)
  - `temp_delta_wind_12h_val`, `temp_delta_wind_12h_is_observed` ($\Delta V_{12\text{h}}$)
  - `temp_delta_pressure_6h_val`, `temp_delta_pressure_6h_is_observed` ($\Delta P_{6\text{h}}$)
  - `temp_wind_change_rate_per_hour_val`, `temp_wind_change_rate_per_hour_is_observed`
  - `temp_delta_ir_min_6h_val`, `temp_delta_ir_min_6h_is_observed`
  - `quality_track_available`

#### 2. Satellite Structural Proxies (38 Features)
- **Source:** NOAA HURSAT-B1 v06 (Geostationary Thermal & Water Vapor NetCDF)
- **Spatial Domain:** $64 \times 64$ grid centered on storm eye (~500 km patch at ~8 km/px resolution).
- **Available Channels:**
  - `IRWIN` (11 µm Window): 100% available in coincident samples.
  - `IRWVP` (6.7 µm Water Vapor): ~96% available.
  - `VSCHN` (0.6 µm Visible): Daytime only (~35–40% available).
- **Physical Feature Families:**
  - Family A (Bulk IR Thermal Moments): Mean, Std, Min, P10, P25, P50, P75, Max, Range, Cold Cloud Fraction ($<233$ K), Very Cold Cloud Fraction ($<219$ K), Overshooting Cloud Fraction ($<203$ K).
  - Family B (Core / Ring Structural Symmetry): Core Mean ($r \le 50$ km), Core Min, Core Cold Fraction, Ring Mean ($50 < r \le 150$ km), Ring Min, Outer Mean ($150 < r \le 250$ km), Radial Contrasts (`core_ring_diff`, `core_outer_diff`), Azimuthal Standard Deviation.
  - Family C (Spatial Texture & Eyewall Gradients): Mean Gradient, Max Eyewall Gradient, Local Spatial Variance, Spatial Entropy.
  - Family D (Tropospheric Water Vapor Contrasts): `has_irwvp`, IRWVP Mean, IRWVP Min, IRWVP Core Mean, IR-WV Differential (`ir_wv_diff_mean`), Core Differential, Spatial Correlation.
  - Family E (Visible Albedo Proxies): `has_vschn`, VSCHN Mean, VSCHN Core Mean, VSCHN Standard Deviation.

---

### Category B: MODEL PREDICTION ARTIFACTS
*Produced strictly by evaluating Frozen Model v3.0.0 on Category A inputs.*
- `model_name`: `CycloneGuard-RI-Multimodal-TS-Final`
- `model_version`: `v3.0.0-frozen`
- `ri_risk_index`: Empirical score $s_{\text{RI}} \in [0, 1]$
- `operating_threshold`: $\tau = 0.125$
- `ri_flag`: Boolean ($s_{\text{RI}} \ge 0.125$)
- `risk_category`: `LOW_RISK` ($<0.125$), `ELEVATED_RISK` ($0.125–0.350$), `HIGH_RISK` ($\ge 0.350$)
- `feature_attributions`: Standardized linear contributions ($w_i \cdot z_i$) separated into Top Supporting and Top Dampening factors.
- **Mandatory Attribution Label:** "Model Feature Attribution — Reflects linear model weights, not physical causality."

---

### Category C: POST-OBSERVATION OUTCOME / VERIFICATION ($t = t_{\text{obs}} + 24\text{h}$)
*STRICTLY FORBIDDEN from entering feature vectors, model loader, or inference pipeline.*
- `future_wind_kts`: Ground-truth maximum sustained wind speed at $t+24$ hours.
- `delta_wind_kts`: Actual observed 24-hour intensification ($\Delta V_{24\text{h}} = V_{t+24\text{h}} - V_t$).
- `ri_target`: Ground-truth binary outcome ($1$ if $\Delta V_{24\text{h}} \ge 30$ kt, else $0$).
- `target_time_utc`: Future timestamp ($t_{\text{obs}} + 24\text{h}$).
- **Mandatory Presentation Label:** "HISTORICAL OUTCOME — NOT USED AS MODEL INPUT".

---

## 4. Disallowed / Excluded Data (Strict Integrity Rules)

1. **Environmental Reanalysis (`env_*`):**
   - Strictly excluded from production inference per Sprint 10 scientific findings.
   - NCEP R2 shear and OISST sea surface temperature must not be represented as inputs to the v3.0.0 model.
2. **Synthetic Satellite Imagery:**
   - Real $64 \times 64$ patch data exists in `data/processed/satellite_patches/`. If an observation lacks patch files, display an honest missing state; NEVER generate AI imagery.
3. **Fabricated Forecast Cones:**
   - No fabricated multi-day track predictions. The forecast horizon is strictly 24 hours for rapid intensification risk.
4. **Calibrated Probability Wording:**
   - Never label the score "Calibrated Probability" or "Chance of RI". The approved term is "Empirical RI Risk Index".

---

## 5. UI Presentation Architecture & Safety Checklist

- [x] **Timeline Selector:** User can click any historical observation fix along the cyclone lifecycle.
- [x] **What the Model Saw Section:** Displays only features from $t \le t_{\text{obs}}$.
- [x] **Model Output Section:** Displays empirical index, $\tau = 0.125$, and feature attribution.
- [x] **Historical Outcome Section:** Visual barrier / toggle clearly demarcating future verification data.
- [x] **Authoritative Precedence Advisory:** Prominently affirms that official IMD / JTWC warnings remain authoritative.
