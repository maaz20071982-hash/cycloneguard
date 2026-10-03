# CycloneGuard Sprint 12 Risk Index Presentation & Threshold Documentation

**Project:** CycloneGuard — AI Early Warning for Rapid Tropical Cyclone Intensification  
**Team:** STORM BYTES  
**Date:** September 2026  
**Status:** Frozen Production Mapping Specification  

---

## 1. Scientific Basis & Calibration Status

The frozen model **`CycloneGuard-RI-Multimodal-TS-Final`** (`v3.0.0-frozen`) outputs an empirical score $S \in [0, 1]$ via regularized logistic regression:

$$S = \sigma\left(\mathbf{w}^T \mathbf{x}_{\text{scaled}} + b\right) = \frac{1}{1 + e^{-(\mathbf{w}^T \mathbf{x}_{\text{scaled}} + b)}}$$

### Calibration Transparency
- **Scientific Finding from Sprint 11:** The validation cohort ($N=42$ with 6 positive RI events) is statistically insufficient to validate post-hoc Platt scaling or isotonic calibration without extreme risk of overfitting or misrepresenting true uncertainty.
- **Strict Terminology Rule:** The score must **NEVER** be presented as a "calibrated probability", "guaranteed likelihood", or "official warning".
- **Approved Terminology:**
  - *"Empirical RI Risk Index"*
  - *"Model-Estimated RI Risk"*
  - *"Empirical Risk Score"*

---

## 2. Operating Threshold Rationale

The frozen production manifest specifies:
$$\tau_{\text{operating}} = 0.125$$

### Justification from Historical Validation
1. **Validation Storm MEGH ($N=42$, 6 RI+):**
   - At $\tau = 0.125$: $\text{Precision} = 1.0000$, $\text{Recall} = 0.5000$, $\text{F1} = 0.6667$, $\text{Accuracy} = 0.9286$, $\text{Brier} = 0.1070$.
   - False Positives: $0$. True Positives: $3$. False Negatives: $3$. True Negatives: $36$.
2. **Untouched Test Storm CHAPALA ($N=53$, 10 RI+):**
   - At $\tau = 0.125$: $\text{Precision} = 1.0000$, $\text{Recall} = 0.2000$, $\text{F1} = 0.3333$, $\text{Accuracy} = 0.8491$, $\text{Brier} = 0.1626$.
   - False Positives: $0$. True Positives: $2$. False Negatives: $8$. True Negatives: $43$.
3. **Dataset Prevalence Context:**
   - Total supervised samples: $N = 299$.
   - Positive RI events ($V_{t+24\text{h}} - V_t \ge 30\text{ kts}$): $39$ ($13.04\%$).
   - A threshold of $0.125$ closely mirrors the empirical prior prevalence ($\approx 13\%$), ensuring that the binary trigger fires only when multi-source features elevate the modeled risk above the baseline rate.

---

## 3. Categorical Presentation Mapping

To assist forecasters while strictly avoiding arbitrary categorization, CycloneGuard maps the continuous index $S$ into three disciplined tiers:

| Category Code | Display Label | Score Range | Meteorological Meaning | Visual Indicator |
| :--- | :--- | :---: | :--- | :--- |
| `LOW_RISK` | **Low Empirical Risk** | $S < 0.125$ | Modeled score is below the operational decision threshold ($\tau=0.125$). Observational kinematic and structural proxies do not indicate rapid intensification conditions within 24 hours. | Neutral / Green (`#16a34a`) |
| `ELEVATED_RISK` | **Elevated Empirical Risk** | $0.125 \le S < 0.350$ | Modeled score meets or exceeds the operational threshold ($\tau=0.125$), indicating statistical alignment with historical RI precursors (deep convective core, rapid pressure drop). Enhanced forecaster vigilance warranted. | Amber / Warning (`#b45309`) |
| `HIGH_RISK` | **High Empirical Risk** | $S \ge 0.350$ | Modeled score is well above operational threshold, placing the observation in the top historical quintile of RI-supportive multimodal signatures. | Red / Alert (`#dc2626`) |

---

## 4. Mandatory Disclaimers & Contextual Notes

Every API response, user interface panel, and admin audit log must bundle the following disclaimers:

1. **Non-Authoritative Warning Disclaimer:**
   > *"This is a model-derived empirical RI risk index, not an official meteorological warning or calibrated probability. Official meteorological warnings issued by RSMC New Delhi (IMD) or JTWC remain authoritative."*
2. **Scientific Horizon & Target Definition:**
   > *"Rapid Intensification is defined strictly as maximum sustained 1-minute wind speed increase $\ge 30\text{ kts}$ within 24 hours ($V_{t+24\text{h}} - V_t \ge 30\text{ kts}$), following WMO / NHC standards (Kaplan & DeMaria 2003)."*
3. **Non-Causality Disclaimer:**
   > *"Standardized linear feature attributions reflect statistical correlation in the frozen regularized logistic regression model. They do not establish physical causation or thermodynamic necessity."*
4. **Data Grounding:**
   > *"Predictions are derived strictly from verified historical observations (NOAA IBTrACS v04r01 best-track and NOAA HURSAT-B1 v06 geostationary imagery). CycloneGuard does not fabricate synthetic sensor inputs."*
