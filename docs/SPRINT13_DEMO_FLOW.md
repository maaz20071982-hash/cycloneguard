# SPRINT 13 — SCIENTIFIC EVIDENCE & HISTORICAL CASE STUDY DEMO FLOW

**Project:** CycloneGuard  
**Role:** Hackathon Judge / Operational Meteorologist Walkthrough  
**Model:** CycloneGuard-RI-Multimodal-TS-Final (`v3.0.0-frozen`)  
**Operating Threshold:** $\tau = 0.125$  
**Evaluation Standard:** Zero Lookahead, Multimodal Evidence Grounding, Traceability  
**Date:** 2026-09-27  

---

## 1. Demo Narrative & Objective

This walkthrough guides an evaluator through the complete evidence-first historical cyclone analysis experience. The objective is to demonstrate that CycloneGuard's intelligence is **understandable, traceable, visually convincing, scientifically honest, and useful during a live operations or hackathon demo**.

### The Core User Journey:
```
CYCLONE DATABASE
   ↓
HISTORICAL OBSERVATION TIMELINE
   ↓
TEMPORAL EVOLUTION & KINEMATICS
   ↓
SATELLITE STRUCTURAL EVIDENCE (HURSAT-B1)
   ↓
MODEL RI RISK INDEX (vs τ = 0.125)
   ↓
MODEL FEATURE ATTRIBUTION
   ↓
HISTORICAL 24H OUTCOME (GROUND TRUTH VERIFICATION)
```

---

## 2. Step-by-Step Judge Walkthrough

### Step 1: Launch and Navigate to Cyclone Database
1. Navigate to the user portal at: `http://localhost:3000/user/cyclones` (or click **Cyclone Database** in navigation).
2. Note the list of **6 historical North Indian Ocean benchmark cyclones** verified against NOAA IBTrACS and HURSAT-B1:
   - **CHAPALA** (2015) — Extremely Severe Cyclonic Storm (61 verified observations, 10 RI+ fixes)
   - **NILOFAR** (2014) — Very Severe Cyclonic Storm (73 verified observations, 11 RI+ fixes)
   - **PHAILIN** (2013) — Extremely Severe Cyclonic Storm (55 verified observations, 11 RI+ fixes)
   - **HUDHUD** (2014) — Destructive Visakhapatnam landfall (66 verified observations, 1 RI+ fix)
   - **MEGH** (2015) — Rapidly developing Socotra storm (49 verified observations, 6 RI+ fixes)
   - **HELEN** (2013) — Pure non-RI benchmark storm (43 verified observations, 0 RI+ fixes)

---

### Step 2: Open Cyclone CHAPALA Case Study
1. In the Cyclone Database table, locate **CHAPALA** and click **Case Study** (or navigate to `/user/cyclones/2015301N11065/case-study`).
2. The **Scientific Historical Case Study Workstation** opens.
3. Observe the Storm Overview Banner:
   - Peak Intensity: **115 kt**
   - Minimum Pressure: **922 hPa**
   - Verified Observations: **61 Fixes**
   - Rapid Intensification Events: **10 RI+ Fixes**

---

### Step 3: Inspect the Historical Observation Timeline
1. Observe the **CycloneTimeline** component across the top:
   - Displays all 61 chronologically sorted fixes from `2015-10-27 12:00 UTC` to `2015-11-04 00:00 UTC`.
   - Each card displays: Observation Time UTC, Coords ($^\circ\text{N}, ^\circ\text{E}$), Current $V_0$, Model RI Risk Index badge, and Satellite Channels (`IR`, `WV`, `VIS`).
2. Select the **Target Fix**: `2015-10-28 18:00:00Z` (13.1°N, 64.6°E, 30 kt).

---

### Step 4: Inspect the Empirical RI Risk Evolution Chart
1. Below the timeline, inspect the **RIRiskTimeline** chart:
   - X-axis: Observation time UTC across the storm lifecycle.
   - Y-axis: **Empirical RI Risk Index** (0.00 to 0.50).
   - Prominent red dashed line: **FROZEN OPERATING THRESHOLD: $\tau = 0.125$**.
   - Shaded green region (below $\tau$) vs shaded pink region (above $\tau$).
   - Point at `2015-10-28 18:00 UTC` clearly spikes to **0.3592** (Well above $\tau$).
   - Points are clickable to switch active analysis fix instantly.

---

### Step 5: Review Prediction vs. Outcome Verification
1. Inspect the two-column **PredictionOutcomeCard**:
2. **Section A (What the Model Saw at $t_0$):**
   - Fix: `2015-10-28 18:00 UTC`
   - Intensity at $t_0$: **30 kt**
   - Central Pressure: **1001 hPa**
   - Empirical RI Risk Index: **0.3592**
   - Threshold: **$\tau = 0.125$**
   - Category: **HIGH_RISK**
3. **Section B (Historical 24h Outcome at $t_0 + 24\text{h}$):**
   - Prominent Header: **"HISTORICAL OUTCOME — NOT USED AS MODEL INPUT"**
   - Verification Time: `2015-10-29 18:00 UTC`
   - Future Intensity ($V_{24}$): **65 kt**
   - Net 24h Intensification ($\Delta V_{24h}$): **+35 kt**
   - WMO RI Criterion: **RAPID INTENSIFICATION OCCURRED (RI+)**
4. **Verification Synthesis Banner:**
   - Highlights: **Scientific Verification: Model Signal Aligned with Outcome** (True Positive detection 24h before Chapala reached hurricane strength).

---

### Step 6: Inspect Temporal Kinematic Indicators
1. Review the **TemporalEvolutionPanel**:
   - Small label: **"Derived from observation history"**
   - Current Intensity ($V_0$): **30 kt** (`track_wind_speed_val`)
   - 12h Prior Wind Change ($\Delta V_{12h}$): **+5 kt** (`temp_delta_wind_12h_val`)
   - Central Pressure ($P_0$): **1001 hPa** (`track_pressure_val`)
   - Vortex Translation: **5.59 kt towards 315.8° (NW motion)**
   - All 23 temporal features map strictly to verified best-track history prior to $t_0$.

---

### Step 7: Inspect Satellite Structural Evidence (NOAA HURSAT-B1)
1. Review the **EvidencePanel**:
   - Source: **NOAA HURSAT-B1 Geostationary Infrared**
   - Active Channels: **IRWIN (11 µm)** and **IRWVP (6.7 µm)**.
   - Channel Status Card: **VSCHN (0.6 µm Visible)** honestly reported as **Nighttime/Unilluminated** (zero fake imagery).
   - Real Satellite Imagery Preview: Renders the authentic $64 \times 64$ infrared patch centered on the vortex with a calibrated Kelvin thermal scale (185 K to 300 K).
   - Extracted Structural Metrics (38 spatial features):
     - Min Brightness $T_b$: **188.2 K** (deep vigorous convective towers)
     - Core Cold Cloud Fraction ($T_b < 233\text{K}$): **61.8%**
     - Overshooting Top Fraction ($T_b < 203\text{K}$): **33.3%**
     - Core-Ring Temperature Gradient: **10.2 K**
     - Azimuthal Symmetry Metric (Core Std): **2.23** (strong axisymmetric organization)

---

### Step 8: Inspect Model Feature Attribution
1. Review the **ModelFeatureAttributionPanel**:
   - Strictly titled: **"Model Feature Attribution"** (NOT "Physical Causality").
   - **Top Supporting Features:**
     - `irwin_overshooting_fraction_203k` ($+0.187$) — Dense convective overshooting tops
     - `irwin_min` ($+0.142$) — Extremely cold cloud tops
     - `temp_delta_wind_12h_val` ($+0.098$) — Prior 12h intensification trend
   - Explanatory note: **"contributed to score"** (describes linear model weighting).
   - Mandatory Scientific Disclaimer:
     *"Attributions describe statistical model behavior within the regularized linear decision space, not physical meteorological causality."*

---

### Step 9: Verify Second Historical Case Study (RI-Negative Baseline)
1. In the breadcrumb, click **Cyclone Database** and select **Cyclone NILOFAR** (`2014297N11062`).
2. Select the pre-intensification fix: `2014-10-23 12:00:00Z` (12.3°N, 64.9°E, 15 kt).
3. Observe:
   - Model RI Risk Index: **0.0002** (Well below operating threshold $\tau = 0.125$).
   - Category: **LOW_RISK**.
   - Historical Outcome: Future wind $V_{24} = 20\text{ kt}$, $\Delta V_{24h} = +5\text{ kt}$ (**RI- Target: 0**).
   - Synthesis: Correctly demonstrated non-RI baseline without issuing false alarm.

---

### Step 10: Inspect Admin Forensic Audit Traceability
1. Navigate to `/admin/predictions` as an authenticated administrator.
2. In the prediction audit table, click **Inspect Audit** on any historical record.
3. The forensic modal opens:
   - **Section A:** Prediction-Time Observational Inputs (available at $t_0$, zero future leakage).
   - **Section B:** Historical Outcome Ground Truth (clearly demarcated as post-event verification).
   - Model Feature Attribution breakdown and provenance metadata.
   - Direct deep-link: **"Open Historical Case Study →"**.

---

## 3. Demo Checklist for Judges

- [x] Evaluates 100% real historical observations (NOAA IBTrACS & HURSAT-B1).
- [x] Zero synthetic satellite imagery generated.
- [x] Model uses frozen 61-feature contract (`CycloneGuard-RI-Multimodal-TS-Final`).
- [x] Operating threshold strictly labeled as $\tau = 0.125$.
- [x] Score strictly labeled as "Empirical RI Risk Index" (NOT "Probability").
- [x] Feature attribution strictly labeled as "Model Feature Attribution" (NOT "Physical Cause").
- [x] Future ground truth ($V_{24}, \Delta V_{24h}$) strictly isolated under "HISTORICAL OUTCOME".
- [x] Full flow completed without touching or opening source code.
