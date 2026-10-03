# Sprint 10 Audit: Baseline Systems, Partitions, and Environmental Requirements

**Audit Date:** 2026-09-27  
**Project:** CycloneGuard — AI Early Warning for Rapid Tropical Cyclone Intensification  
**Team:** STORM BYTES  
**Phase:** Sprint 10 — Phase 1 Deliverable  

---

## 1. Executive Summary

This audit establishes the baseline scientific, algorithmic, and data architecture of CycloneGuard prior to any Sprint 10 modifications. Sprint 9 successfully established that while standalone satellite spatial features perform poorly out-of-sample (ROC-AUC 0.4488), combining spatial satellite proxies with temporal kinematics (Model ST) substantially suppresses false alarms (14 false positives reduced to 3) and elevates PR-AUC from 0.3808 to 0.4086 on the held-out test storm **CHAPALA**.

Sprint 10 poses the core research question:
> **"Do large-scale environmental conditions provide independent predictive information for Rapid Intensification when combined with temporal cyclone evolution and satellite structural evidence?"**

This audit cataloged all existing datasets, models, schemas, invariants, and environmental data requirements to ensure strict zero-leakage compliance, complete non-fabrication of environmental variables, and scientific integrity.

---

## 2. Current Dataset State

The current verified dataset was expanded in Sprint 8 and audited in Sprint 9:

| Metric | Verified Value | Notes / Source |
| :--- | :--- | :--- |
| **Historical Basins** | North Indian Ocean (NIO: Bay of Bengal & Arabian Sea) | WMO official basin boundaries |
| **Unique Storm Lifecycles** | 6 storms | PHAILIN, HELEN, HUDHUD, NILOFAR, MEGH, CHAPALA |
| **Raw HURSAT NetCDF3 Files** | 887 files validated | NOAA NCEI HURSAT-B1 archive v06 |
| **Coincident Observations** | 347 fixes | 3-hourly track alignment with $\Delta t \le 1.5\text{h}, \Delta r \le 50\text{km}$ |
| **Physical 64×64 Patches** | 1,020 extracted patches | 347 IRWIN (10.8 µm), 338 IRWVP (6.7 µm), 335 VSCHN (0.6 µm) |
| **Supervised RI Samples** | 299 samples | Samples with valid $t+24\text{h}$ track and known RI target |
| **Unlabeled / Boundary Fixes** | 48 samples | Storm dissipation / landfall within 24h of fix time |
| **RI Positive Samples (RI+)** | 39 samples (13.04% prevalence) | Severe class imbalance ($\Delta V_{24\text{h}} \ge 30\text{ kts}$) |
| **RI Negative Samples (RI-)** | 260 samples (86.96% prevalence) | Non-intensifying or slow-intensifying fixes |

---

## 3. Storm-Wise Partitions (Strict Isolation)

Splits are strictly disjoint at the whole-cyclone lifecycle level. Under no circumstances are observations randomly shuffled across partitions.

| Partition | Storm Name | Season | Basin | Supervised Fixes | RI+ | RI- | Prevalence | Role in Sprint 10 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **TRAIN** | PHAILIN | 2013 | Bay of Bengal | 64 | 7 | 57 | 10.94% | Feature fitting & model training |
| **TRAIN** | HELEN | 2013 | Bay of Bengal | 36 | 1 | 35 | 2.78% | Feature fitting & model training |
| **TRAIN** | HUDHUD | 2014 | Bay of Bengal | 58 | 10 | 48 | 17.24% | Feature fitting & model training |
| **TRAIN** | NILOFAR | 2014 | Arabian Sea | 46 | 5 | 41 | 10.87% | Feature fitting & model training |
| **VAL** | MEGH | 2015 | Arabian Sea | 42 | 6 | 36 | 14.29% | Hyperparameter & threshold selection only |
| **TEST** | CHAPALA | 2015 | Arabian Sea | 53 | 10 | 43 | 18.87% | **Untouched benchmark test storm** |
| **TOTAL** | **6 Storms** | — | — | **299** | **39** | **260** | **13.04%** | — |

*Partition Invariants Confirmed:*
- $\text{Train} \cap \text{Val} = \emptyset$
- $\text{Train} \cap \text{Test} = \emptyset$
- $\text{Val} \cap \text{Test} = \emptyset$
- Cross-partition satellite asset overlap: 0 files.
- Cross-partition physical patch overlap: 0 patches.

---

## 4. Existing Feature Groups

1. **Temporal / Kinematic Features (23 features, Sprint 6 subset_b):**
   - Current intensity ($V_{\text{max}}$ in kts) and observation presence flag.
   - Current central pressure (MSLP in hPa) and presence flag.
   - Current center coordinates (Latitude, Longitude) and presence flags.
   - Translation kinematics: translation speed (kts), translation bearing (degrees), and flags.
   - Short-term intensification momentum: $\Delta V_{6\text{h}}$, $\Delta V_{12\text{h}}$, $\Delta P_{6\text{h}}$, wind change rate per hour, and presence flags.
   - Track quality and availability indicators.
2. **Spatial Satellite Features (38 features, Sprint 9 Families A–E):**
   - *Family A (Bulk IR Stats, 12 feats):* Mean, std, min, max, temp range, percentiles (p10, p25, p50, p75), cold cloud fractions ($T \le 233.15\text{K}$, $T \le 219.15\text{K}$, $T \le 203.15\text{K}$).
   - *Family B (Core/Ring Structural Proxies, 11 feats):* Core mean/min/cold-fraction ($r \le 50\text{km}$), Ring mean/min/cold-fraction ($50 < r \le 150\text{km}$), Outer mean ($150 < r \le 250\text{km}$), Radial contrasts ($\overline{T}_{\text{ring}} - \overline{T}_{\text{core}}$, $\overline{T}_{\text{outer}} - \overline{T}_{\text{core}}$), Azimuthal asymmetry.
   - *Family C (Texture & Gradients, 4 feats):* Sobel gradient mean and max, local variance ($5\times 5$), spatial entropy.
   - *Family D (Multispectral IR/WV, 7 feats):* `has_irwvp`, IRWVP mean, min, core mean, IR-WV spectral difference, core difference, spatial correlation.
   - *Family E (Visible Channel, 4 feats):* `has_vschn`, visible albedo mean, core mean, std (NaN during night passes; never zero-filled).

---

## 5. Existing Model Artifacts & Baselines

All existing artifacts are preserved under `models/ri/`:
- `models/ri/v1/`: Sprint 6 Model B (Temporal kinematics, 23 features, logistic regression).
- `models/ri/v2_spatial/`: Sprint 9 Model S (38 spatial features, logistic regression, test ROC-AUC 0.4488, PR-AUC 0.1777).
- `models/ri/v2_combined/`: Sprint 9 Model ST (61 temporal + spatial features, logistic regression, test ROC-AUC 0.7279, PR-AUC 0.4086, Accuracy 83.02%, Precision 57.14%, Brier 0.1356).

---

## 6. Environmental Data Requirements for Sprint 10

To evaluate whether large-scale environmental context provides independent predictive value, candidate environmental variables must fulfill strict physical and temporal criteria:

1. **Vertical Wind Shear (VWS):**
   - *Physical Definition:* Vector difference between upper-tropospheric wind ($200\text{ hPa}$) and lower-tropospheric wind ($850\text{ hPa}$):
     $$\vec{V}_{\text{shear}} = \vec{V}_{200} - \vec{V}_{850}$$
     $$\text{Shear Magnitude} = \|\vec{V}_{200} - \vec{V}_{850}\| = \sqrt{(u_{200} - u_{850})^2 + (v_{200} - v_{850})^2}$$
   - *Physical Unit:* Knots or meters per second ($1\text{ m/s} \approx 1.94384\text{ kts}$).
   - *Meteorological Significance:* Low shear ($< 15\text{ kts}$) permits vertical alignment of the convective core and latent heat retention; strong shear ($> 20\text{ kts}$) tilts the vortex, ventilates the warm core with dry environmental air, and suppresses RI.
2. **Sea Surface Temperature (SST):**
   - *Physical Definition:* Temperature of the ocean skin/sub-surface layer.
   - *Physical Unit:* Degrees Celsius (°C) or Kelvin (K).
   - *Meteorological Significance:* SST $\ge 26.5^\circ\text{C}$ is a thermodynamic prerequisite for tropical cyclogenesis and RI; higher SSTs increase the thermodynamic Maximum Potential Intensity (MPI).
3. **Mid-Tropospheric Relative Humidity (RH):**
   - *Physical Definition:* Relative humidity at $700\text{ hPa}$ or $500\text{ hPa}$ in the inner/outer cyclone environment.
   - *Physical Unit:* Percent (%).
   - *Meteorological Significance:* Dry air intrusion inhibits convective buoyancy and induces downdrafts that weaken the core.

---

## 7. Zero-Leakage & Integrity Safeguards for Environmental Ingestion

1. **Strict Temporal Bound ($t \le t_0$):**
   - For an observation at time $t_0$, environmental data must be sampled at $t_{\text{env}} \le t_0$ or within an explicitly bounded synoptic tolerance ($\Delta t \le \pm 1.0\text{h}$).
   - **Never** use environmental reanalysis fields from $t_0 + 6\text{h}$, $t_0 + 12\text{h}$, or $t_0 + 24\text{h}$.
2. **Strict Spatial Localization:**
   - Environmental values must be sampled at the exact IBTrACS fix coordinates $(\text{lat}_0, \text{lon}_0)$ corresponding to $t_0$.
3. **Explicit Missingness Indicators:**
   - If an environmental variable is missing or landlocked (e.g. SST over land when a cyclone moves inland), the feature must be flagged with `is_observed = 0.0` and the value set to NaN. **Zero-filling is strictly forbidden**.
4. **Train-Only Preprocessing:**
   - All imputers, normalizers, and scalers must be fitted **exclusively on the 4 training storms** and applied blindly to validation (Megh) and test (Chapala).
5. **No Test-Storm Tuning:**
   - Decision thresholds must be selected exclusively using validation storm Megh; Chapala remains untouched.

---

## 8. Expected Blockers & Contingency Strategy

- **Blocker A: Network Access Restrictions:** If scientific servers cannot be reached or fail to provide historical grids for 2013–2015, the project will immediately declare **Outcome B (Data Unavailable)** and document the blocker rather than creating synthetic values.
- **Blocker B: Landfall Contamination:** As storms make landfall (e.g. Phailin over Odisha, India), marine variables like SST become physically undefined. The pipeline must handle land values cleanly without crashing or corrupting adjacent ocean points.
- **Blocker C: Small Sample Scale:** With only 39 RI-positive samples across 6 storms, adding too many environmental dimensions could cause over-parameterization. Therefore, a strictly parsimonious set of 4–6 environmental variables must be enforced.
