# CycloneGuard Multi-Source Data Fusion Methodology

**Sprint:** 5 — AI Data Fusion & Cyclone State Engine  
**Status:** Approved & Frozen

---

## 1. Fusion Philosophy & Scientific Rules

Traditional machine learning systems often either:
1. Concatenate raw multi-sensor arrays into monolithic deep neural networks, causing silent failure when an operational satellite overpass is delayed; or
2. Impute missing sensors with zero values, causing the neural network to confuse "zero wind speed" with "no scatterometer pass."

CycloneGuard enforces a **scientifically inspectable feature-level fusion paradigm**:

```
MULTI-SOURCE OBSERVATIONS (IBTrACS, HURSAT, INSAT, ASCAT, GMI)
                    ↓
TEMPORAL ALIGNMENT (Nearest-neighbor with strict tolerance windows)
                    ↓
SPATIAL ALIGNMENT (Cyclone-centered 101x101 coordinate extraction)
                    ↓
FEATURE EXTRACTION (Track, Radiometric, Morphology, Temporal, Quality)
                    ↓
SOURCE-SPECIFIC FEATURES (Inspectable physical and statistical variables)
                    ↓
CROSS-SOURCE FUSION & QUALITY AUDIT (Scientific plausibility checks)
                    ↓
CYCLONE STATE VECTOR (69-dim vector with dual value/indicator channels)
                    ↓
DOWNSTREAM AI MODELS (Baseline Classifier, Future Forecasting Networks)
```

---

## 2. Multi-Source Integration Strategy

### Actual Availability Audit (Sprint 5)
As proven in [`docs/SPRINT5_DATA_AUDIT.md`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/docs/SPRINT5_DATA_AUDIT.md):
- **NOAA IBTrACS** is CONNECTED (400 validated track points across 10 North Indian Ocean storms).
- **NOAA HURSAT-B1** is CONNECTED (101x101 storm-centered IR grid for Cyclone Mocha).
- **INSAT MOSDAC, ADT Dvorak, MetOp ASCAT, GPM GMI** are unbundled external assets currently flagged as unobserved.

### Architectural Rule: No Synthetic Multi-Source Fabrication
When external sensors are unavailable:
- The pipeline **does not fabricate** synthetic brightness temperatures, scatterometer wind vectors, or radar rain rates.
- Unobserved sensor fields are explicitly populated with `None` in `CycloneState`.
- In the numerical feature vector, the feature's `is_observed` flag is set to `0.0`, and its fallback value is filled with the training-split median.
- Cross-sensor comparison fields evaluate to `"insufficient_evidence"`.

---

## 3. Cross-Source Physical Consistency Engine

Implemented in [`ml/features/cross_source.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/features/cross_source.py), cross-source fusion evaluates concordance between physically related parameters:

### 1. Objective Intensity vs. Ground Truth
When both satellite objective intensity (ADT) and best-track intensity (IBTrACS) exist:
$$\Delta V_{\text{intensity}} = V_{\text{ADT}} - V_{\text{IBTrACS}}$$
- $|\Delta V| \le 10\,\text{kts} \implies$ `consistent`
- $10 < |\Delta V| \le 20\,\text{kts} \implies$ `partially_consistent`
- $|\Delta V| > 20\,\text{kts} \implies$ `disagreeing`
- *Missing either sensor* $\implies$ `insufficient_evidence`

### 2. Deep Convection vs. Surface Wind Speed Plausibility
Compares the fraction of cold convective cloud tops ($T_b < 210\,\text{K}$) against reported wind speed:
- If reported wind speed $V \ge 65\,\text{kts}$ (hurricane strength) and convective fraction $f_{210\text{K}} \ge 0.05 \implies \text{Plausibility} = 1.0$.
- If $V \ge 65\,\text{kts}$ but $f_{210\text{K}} < 0.01$ (high wind reported with zero cold cloud) $\implies \text{Plausibility} = 0.3$ (physical anomaly/possible shear).
- If satellite imagery is absent $\implies \text{Plausibility} = \text{null}$.

---

## 4. Handling Missing Data (Value + Availability Channel)

Rather than naive zero-imputation, every numerical feature $x_i$ is mapped into a 2-tuple:
$$(x_{i,\text{val}}, x_{i,\text{is\_observed}})$$

```python
if raw_value is not None:
    val_float = float(raw_value)
    is_obs = 1.0
else:
    val_float = training_median.get(feature_name, 0.0)
    is_obs = 0.0
```

This guarantees:
1. Linear models can learn independent weights for feature presence vs feature magnitude.
2. Tree-based algorithms can split on sensor availability.
3. Future neural models can mask unobserved channels via attention or gating mechanisms.

---

## 5. Normalization & Scaler Discipline

Implemented in [`ml/features/scaler.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/features/scaler.py):
- **Training-Only Fit:** Scalers are fitted **strictly on the training partition**. Validation and test partitions are transformed using the training parameters.
- **Binary Indicator Protection:** Feature columns ending in `_is_observed` or starting with `quality_` are exempted from scaling, preserving their exact $\{0.0, 1.0\}$ domain.
- **Serialization:** Scaler means, variances, and column masks are exported to `scaler.json` for deterministic inference.
