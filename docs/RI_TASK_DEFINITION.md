# CycloneGuard Rapid Intensification (RI) Learning Task Definition

**Sprint:** 6 — Rapid Intensification Model v1  
**Document:** `docs/RI_TASK_DEFINITION.md`  
**Status:** Approved & Frozen

---

## 1. Learning Task Formulation

The Rapid Intensification (RI) prediction task is formulated as a binary classification problem:

Given the observed cyclone state $\mathbf{s}(t_0)$ and retrospective temporal history $\{\mathbf{s}(t) \mid t \le t_0\}$ available at observation time $t_0$, predict whether the tropical cyclone will undergo rapid intensification over a forward forecast horizon $H \in \{12, 24, 36, 48\}\,\text{hours}$:

$$P(y_H = 1 \mid \mathbf{s}(t_0), \mathbf{s}_{t \le t_0})$$

Where:
- $y_H \in \{0, 1\}$ is the binary ground-truth RI outcome.
- $t_0$ is the current analysis timestamp.
- $H$ is the forecast lead time (operational primary horizon: $H = 24.0\,\text{hours}$).

---

## 2. Mathematical Labeling Rules

Ground-truth labels are computed from verified best-track intensity series (NOAA IBTrACS) without forward interpolation:

$$\Delta V_H(t_0) = V(t_0 + H) - V(t_0)$$

$$y_H(t_0) = \begin{cases} 
1, & \text{if } \Delta V_H(t_0) \ge \Theta_H \\ 
0, & \text{if } \Delta V_H(t_0) < \Theta_H \\ 
\text{null}, & \text{if future observation } V(t_0 + H) \text{ is missing/unavailable}
\end{cases}$$

### Configured Operational Thresholds ($\Theta_H$):
| Horizon ($H$) | Threshold ($\Theta_H$) | Physical Variable | Meteorological Reference |
|---|---|---|---|
| **12 Hours** | $\ge 20.0\,\text{kts}$ | $\Delta V_{12h}$ (1-min sustained wind) | Secondary early warning indicator |
| **24 Hours** | $\ge 30.0\,\text{kts}$ | $\Delta V_{24h}$ (1-min sustained wind) | **Kaplan & DeMaria (2003); WMO / NHC standard** |
| **36 Hours** | $\ge 40.0\,\text{kts}$ | $\Delta V_{36h}$ (1-min sustained wind) | Medium-range operational benchmark |
| **48 Hours** | $\ge 50.0\,\text{kts}$ | $\Delta V_{48h}$ (1-min sustained wind) | Extended-range operational benchmark |

---

## 3. Observation & Temporal Matching Requirements

1. **Tolerance Window:** An observation at $t_{\text{future}}$ is accepted as the ground truth for $t_0 + H$ if and only if:
   $$|t_{\text{future}} - (t_0 + H)| \le \Delta t_{\text{tol}}$$
   Where $\Delta t_{\text{tol}} = 2.0\,\text{hours}$ for $H=12, 24\text{h}$ and $3.0\,\text{hours}$ for $H=36, 48\text{h}$.
2. **Nearest Valid Point:** If multiple records fall within the tolerance window, the point with minimal $|t_{\text{future}} - (t_0 + H)|$ is selected.
3. **Valid Physical Measurements:** Both $V(t_0)$ and $V(t_0 + H)$ must be finite, valid numbers ($0 \le V \le 250\,\text{kts}$). If either is unrecorded or invalid, the label is uncomputable.

---

## 4. Exclusion Rules & Missing-Label Handling

### Exclusion Criteria:
1. **Trailing Track Points (Landfall or Dissipation):** When a cyclone makes landfall or dissipates before $t_0 + H$, no verified marine track point exists.
   - Status: Marked as `UNAVAILABLE_MISSING_FUTURE`.
   - Treatment: **Completely excluded from supervised training and test evaluation.**
   - Strictly forbidden: Linear extrapolation or synthetic future label imputation.
2. **Missing Initial Intensity:** If $V(t_0)$ is null or unrecorded in best-track records.
   - Status: Marked as `UNAVAILABLE_MISSING_CURRENT`.
   - Treatment: Excluded from supervised training.

---

## 5. Empirical Class Balance & Sampling

Across the 400 track points in the North Indian Ocean dataset:

| Horizon | Total Track Points | Supervised Samples | RI Events ($y=1$) | Non-RI ($y=0$) | Prevalence |
|---|---|---|---|---|---|
| **12h** | 400 | 341 | 22 | 319 | **6.45%** |
| **24h** | 400 | 303 | 29 | 274 | **9.57%** |
| **36h** | 400 | 274 | 29 | 245 | **10.58%** |
| **48h** | 400 | 242 | 27 | 215 | **11.16%** |

### Imbalance Mitigation Strategy:
Because RI occurs in only ~9.6% of valid 24h observations, models cannot rely on standard accuracy or symmetric loss functions. The learning task requires:
1. **Balanced Class Weighting:** Loss is weighted inversely proportional to class frequencies:
   $$w_1 = \frac{N}{2 \cdot N_{\text{pos}}}, \quad w_0 = \frac{N}{2 \cdot N_{\text{neg}}}$$
2. **Precision-Recall Focused Metrics:** Primary optimization on PR-AUC, Recall at target precision, and F1 score rather than overall accuracy.
3. **Threshold Optimization:** Deriving operational decision thresholds $\theta$ from the validation set to balance false alarms against missed detections.

---

## 6. Strict Data Leakage Prevention Firewalls

1. **Temporal Precedence:** All features used to construct $\mathbf{x}(t_0)$ must have timestamps $t \le t_0$.
2. **Strict Future Target Horizon:** The target interval begins strictly at $t_0$ and evaluates at $t_0 + H$.
3. **Target Variable Separation:** $\Delta V_H$, $V(t_0 + H)$, and $y_H$ are never included in feature definitions, registries, encoders, or state vectors.
4. **Storm-Wise Isolation:** Observations from the same tropical cyclone (same `storm_id`) are constrained to exactly one partition (`train`, `val`, or `test`).
