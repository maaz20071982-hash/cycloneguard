# CycloneGuard Storm-Wise Dataset Splitting Specification

**Sprint:** 6 — Rapid Intensification Model v1  
**Config File:** [`ml/config/split_config.json`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/config/split_config.json)  
**Status:** Approved & Frozen

---

## 1. Rationale for Storm-Wise Partitioning

In meteorology and atmospheric machine learning, **random sample-level train/test splits are strictly invalid**. 

Because tropical cyclones are highly continuous spatio-temporal systems with significant temporal autocorrelation:
1. Observations from the same storm taken 3 hours apart have nearly identical environmental shear, SST, and core structures.
2. A random train/test split allows a model to "cheat" by memorizing the unique trajectory and background environment of an individual cyclone.
3. Such models achieve deceptively high cross-validation scores (~95% accuracy) but fail completely when deployed operationally on a newly formed cyclone.

**CycloneGuard Rule:** Partitioning is performed **strictly by storm identity (`storm_id`)**. All track fixes, satellite passes, and temporal features from any given cyclone belong to **exactly one partition**.

---

## 2. Partition Composition & Distribution

| Partition | Storm ID | Storm Name | Total Points | 24h Supervised Points | RI Events ($y=1$) | Class Balance |
|---|---|---|---|---|---|---|
| **TRAIN** | `2023293N12089` | **HAMOON** | 41 | 35 | 5 | 14.3% RI |
| | `2023160N20092` | UNNAMED | 15 | 11 | 0 | 0.0% RI |
| | `2023156N10067` | **BIPARJOY** | 113 | 98 | 0 | 0.0% RI (Gradual) |
| | `2023292N11063` | **TEJ** | 43 | 36 | 10 | 27.8% RI |
| | `2023273N16073` | UNNAMED | 8 | 4 | 0 | 0.0% RI |
| | `2023334N08088` | **MICHAUNG** | 31 | 22 | 0 | 0.0% RI |
| | `2023317N10094` | **MIDHILI** | 39 | 21 | 0 | 0.0% RI |
| *Train Subtotal* | **7 Storms** | — | **290** | **227** | **15** | **6.61% RI** |
| **VAL** | `2023212N19090` | UNNAMED | 31 | 18 | 0 | 0.0% RI |
| | `2023030N08087` | UNNAMED | 28 | 15 | 3 | 20.0% RI |
| *Val Subtotal* | **2 Storms** | — | **59** | **33** | **3** | **9.09% RI** |
| **TEST** | `2023129N08091` | **MOCHA** | 51 | 43 | 11 | **25.58% RI** |
| *Test Subtotal* | **1 Storm** | — | **51** | **43** | **11** | **25.58% RI** |
| **TOTAL** | **10 Storms** | — | **400** | **303** | **29** | **9.57% RI** |

---

## 3. Justification for Test Storm Selection (Cyclone Mocha)

Cyclone Mocha was designated as the primary held-out test case because:
1. **Extreme RI Benchmark:** Mocha was the most intense cyclone in the North Indian Ocean during 2023, undergoing extreme RI from 70 kts to 140 kts within 24 hours ($\Delta V_{24h} = +70\,\text{kts}$). Testing on Mocha provides an uncompromising assessment of whether models can anticipate true extreme events.
2. **Multi-Platform Satellite Coincidence:** Mocha is the only storm in the current dataset possessing coincident HURSAT-B1 high-resolution infrared imagery, enabling full-spectrum evaluation of Model C (multi-source fusion).
3. **Completely Unseen:** Zero observations from Mocha are ever seen during feature scaling, hyperparameter selection, threshold tuning, or model fitting.

---

## 4. Mathematical Leakage Invariants & Unit Verification

The dataset splitting logic enforces three mathematical invariant assertions:

$$\mathcal{S}_{\text{train}} \cap \mathcal{S}_{\text{val}} = \emptyset$$
$$\mathcal{S}_{\text{train}} \cap \mathcal{S}_{\text{test}} = \emptyset$$
$$\mathcal{S}_{\text{val}} \cap \mathcal{S}_{\text{test}} = \emptyset$$

```python
train_ids = set(config["train_storms"])
val_ids = set(config["val_storms"])
test_ids = set(config["test_storms"])

assert train_ids.isdisjoint(val_ids), "Data leakage: Train and Val share storm IDs!"
assert train_ids.isdisjoint(test_ids), "Data leakage: Train and Test share storm IDs!"
assert val_ids.isdisjoint(test_ids), "Data leakage: Val and Test share storm IDs!"
```
All tests enforce these assertions unconditionally.
