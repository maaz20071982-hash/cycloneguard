# Scientific Limitations & Operational Disclaimers — Sprint 6

Under CycloneGuard's core scientific principles, all limitations, uncertainties, and constraints must be explicitly documented without obfuscation. Transparent recognition of statistical boundaries is essential for trustworthy artificial intelligence in meteorological operations.

---

## 1. Dataset Scale & Statistical Power

* **Sample Size Constraint:** The historical supervised dataset comprises **10 tropical cyclones** spanning 400 total observational fixes from the 2023 North Indian Ocean season.
* **Effective Supervised Instances:** At the operational 24-hour forecast horizon ($\Delta t = 24\text{h}$ with a $\pm 2.5\text{h}$ pairing window), only **303 observations** have valid forward verification points.
* **Positive Event Scarcity:** Across the 303 supervised observations, only **29 instances (9.57%)** satisfied the WMO/NHC criterion for Rapid Intensification ($\Delta V_{24h} \ge 30\,\text{kts}$).
* **Implications:** Statistical power is constrained. Complex nonlinear estimators and deep recurrent neural networks (LSTM/GRU/Transformers) with thousands of trainable parameters cannot be robustly fit without severe memorization.

---

## 2. Storm Diversity & Partition Imbalance

* **Storm-Wise Partitioning:** In compliance with strict zero-leakage standards, observations are partitioned strictly by whole cyclone life-cycles:
  * **Training Split (7 storms, 227 supervised samples):** 18 positive RI events (7.9% prevalence).
  * **Validation Split (2 storms, 33 supervised samples):** **0 positive RI events (0.0% prevalence).**
  * **Held-Out Test Split (1 storm — Cyclone Mocha, 43 supervised samples):** 11 positive RI events (25.6% prevalence).
* **Validation Partition Zero-Positive Anomaly:** Because storms in the validation partition (e.g., 2023030N08087, 2023212N19090) did not undergo rapid intensification during their 24h tracked life-cycle, the validation set has a 0% base rate. Consequently, validation ROC-AUC and PR-AUC are mathematically undefined or trivial on this split.
* **Test Concentration:** Evaluation is heavily indexed on Cyclone Mocha (`2023129N08091`), an Extremely Severe Cyclonic Storm in the Bay of Bengal. While Mocha provides an exceptional case study of explosive intensification (peak $V_{\text{max}} = 130\,\text{kts}$), it represents a single meteorological system.

---

## 3. Geographic Coverage & Basin Specificity

* **North Indian Ocean Exclusivity:** All training and evaluation data originate strictly from the North Indian Ocean basin (Bay of Bengal and Arabian Sea).
* **Non-Generalizability:** Atmospheric boundary conditions in the North Indian Ocean (monsoon trough dynamics, high sea surface salinity gradients, distinct vertical wind shear regimes) differ significantly from the Western North Pacific (typhoons) and North Atlantic (hurricanes). The model cannot be assumed to generalize to other ocean basins without re-training and re-benchmarking.

---

## 4. Satellite Sensor Availability & Spatial-Temporal Gaps

* **Infrared Imagery Sparsity:** Across the 400 track fixes in the verified sample dataset, coincident 10.8 µm thermal infrared geostationary imagery (NOAA HURSAT-B1) is available for only **1 fix** (Cyclone Mocha at 2023-05-12 00:00 UTC). The remaining 99.75% of fixes lack coincident satellite imagery.
* **Passive Microwave Sounders:** 100% of observations in the historical sample lack coincident overpasses from polar-orbiting microwave radiometers (GPM GMI, MetOp ASCAT, Megha-Tropiques SAPHIR).
* **Operational Implication:** Model C (Multi-Source Evidence) currently achieves identical metrics to Model B (Temporal Kinematics) because missing sensors are truthfully flagged rather than synthetically filled. The model is currently operating almost entirely on track kinematics and temporal rate-of-change.

---

## 5. Temporal Gaps & Re-Centering Uncertainty

* **Fix Regularity:** Synoptic best-track fixes occur at 3-hour or 6-hour intervals. Intermediate intensification episodes between synoptic fixes are linearly interpolated or unobserved.
* **Center Localization Noise:** Historical best-track center coordinates have an estimated positional uncertainty of $\pm 15$ to $\pm 35\,\text{km}$ depending on system organization (Dvorak technique vs. microwave fix).

---

## 6. Label Uncertainty & Dvorak Limitations

* **Subjective Ground Truth:** Unlike aircraft reconnaissance flights (regularly deployed in the Atlantic), North Indian Ocean intensity values rely predominantly on satellite Dvorak techniques and RSMC New Delhi synoptic advisories. Best-track wind estimates have an inherent observational uncertainty of approximately $\pm 5$ to $\pm 10\,\text{kts}$.
* **Threshold Edge Cases:** A storm intensifying by $29\,\text{kts}$ in 24 hours is labeled non-RI (`0`), whereas a storm intensifying by $30\,\text{kts}$ is labeled RI (`1`). This strict binary discretization introduces label noise near the $30\,\text{kts}$ boundary.

---

## 7. Probability Calibration Limitations

* **Uncalibrated Model Scores:** Platt scaling (logistic sigmoid regression over raw model scores) requires positive and negative examples in the calibration split to estimate valid scale and shift parameters. Because the validation split contained zero positive RI events, fitting Platt scaling or isotonic regression on validation data was statistically invalid.
* **User Portal Phrasing:** Model outputs must be interpreted as **uncalibrated empirical ranking scores**, NOT true frequentist Bayesian probabilities. They are explicitly displayed as "Model RI Score: X" rather than "X% chance".

---

## 8. Operational & Real-Time Deployment Boundaries

* **No Real-Time Ingestion Feed:** CycloneGuard is currently validated on staged historical data. It does not possess an active, authenticated real-time telemetry stream from IMD GTS or ISRO MOSDAC servers.
* **Non-Operational Status:** CycloneGuard is an academic research and technical demonstration platform. It must **NEVER** be used as a primary decision-making tool for disaster management, maritime navigation, or public evacuation.
* **Official Warning Primacy:** Official tropical cyclone advisories, track forecasts, and evacuation orders remain the sole legal authority of national meteorological agencies (RSMC New Delhi / India Meteorological Department).
