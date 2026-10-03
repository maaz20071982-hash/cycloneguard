# CycloneGuard Rapid Intensification (RI) Label Definition & Architecture

**Sprint:** 5 — AI Data Fusion & Cyclone State Engine  
**Configuration File:** [`configs/ri_config.yaml`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/configs/ri_config.yaml)  
**Implementation:** [`ml/data/sequences/ri_label.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/data/sequences/ri_label.py)

---

## 1. Scientific Justification & Operational Definition

Rapid Intensification (RI) is the primary driver of catastrophic tropical cyclone forecasting failures. CycloneGuard adheres to the internationally recognized standard formulated by Kaplan & DeMaria (2003) and adopted by the World Meteorological Organization (WMO) and the National Hurricane Center (NHC):

$$\Delta V_{24\text{h}} = V(t_0 + 24\,\text{h}) - V(t_0) \ge 30\,\text{knots}$$

Where:
- $V(t_0)$ is the maximum sustained wind speed (knots) at observation time $t_0$.
- $V(t_0 + 24\,\text{h})$ is the verified maximum sustained wind speed (knots) exactly 24 hours later.
- $\Delta V_{24\text{h}}$ is the intensity change over the 24-hour horizon.

### Alternative Horizons & Sensitivity
While the primary operational benchmark is 24 hours / 30 knots, [`configs/ri_config.yaml`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/configs/ri_config.yaml) supports parameterized sensitivity studies:
- **12-hour horizon:** $\Delta V_{12\text{h}} \ge 20\,\text{knots}$
- **36-hour horizon:** $\Delta V_{36\text{h}} \ge 40\,\text{knots}$
- **48-hour horizon:** $\Delta V_{48\text{h}} \ge 50\,\text{knots}$

---

## 2. Empirical Grounding on Actual Dataset (North Indian Ocean 2023)

To ensure scientific honesty, the RI label generator was audited against the entire verified best-track dataset (NOAA IBTrACS, 10 storms in 2023, 400 track points):

```
Total Track Points Analyzed:          400
Track Points with Valid 24h Future:   303
Trailing Track Points (Landfall/End):  97 (marked UNAVAILABLE_MISSING_FUTURE)

Class Distribution on Supervised Points:
├── Rapid Intensification (RI = 1):    29 points  ( 9.57%)
└── Non-Rapid Intensification (RI = 0): 274 points (90.43%)
```

### Key Scientific Observations:
1. **Natural Imbalance:** The positive class frequency (~9.6%) mirrors real-world meteorological climatology. RI is an extreme, low-probability, high-impact phenomenon.
2. **Mocha Extreme RI:** Very Severe Cyclonic Storm Mocha underwent an extreme RI phase, accelerating from 70 kts to 140 kts within 24 hours ($\Delta V_{24\text{h}} = +70\,\text{kts}$), providing an ideal held-out test case for evaluating representation power.
3. **Biparjoy Prolonged Moderate Rate:** Very Severe Cyclonic Storm Biparjoy intensified gradually, spending prolonged periods in the non-RI regime ($\Delta V_{24\text{h}} \approx 10\text{--}20\,\text{kts}$).

---

## 3. Strict Missing-Future Protocol (No Interpolation)

A common mistake in cyclone modeling is interpolating future track points when a storm dissipates or makes landfall within 24 hours of $t_0$.

**CycloneGuard Rule:**
- If an actual verified observation does not exist within the $[22\,\text{h}, 26\,\text{h}]$ future tolerance window, the label is marked `UNAVAILABLE_MISSING_FUTURE`.
- `target_is_ri` is set to `None`.
- `delta_wind_kts` is set to `None`.
- These points are excluded from supervised evaluation to prevent target leakage or fictitious label generation.

---

## 4. Configuration Schema (`configs/ri_config.yaml`)

```yaml
version: "1.0.0"
target_name: "rapid_intensification_24h"

default_definition:
  horizon_hours: 24.0
  threshold_value: 30.0
  threshold_unit: "knots"
  variable: "maximum_sustained_wind_speed"
  scientific_reference: "Kaplan & DeMaria (2003); WMO / NHC standard"
  tolerance_window_hours: 2.0

evaluation_protocol:
  metrics:
    - "precision"
    - "recall"
    - "f1"
    - "pr_auc"
    - "roc_auc"
    - "confusion_matrix"
  primary_optimization_metric: "f1"
```
