# Sprint 10 Environmental Feature Registry

**Document Version:** 1.0  
**Phase:** Sprint 10 — Phase 4 Deliverable  
**Module:** [`ml/features/environmental.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/features/environmental.py)  

---

## 1. Overview

The Environmental Feature Registry catalogues the 13 large-scale atmospheric and oceanic variables engineered to capture environmental favorability for tropical cyclone Rapid Intensification (RI, $\Delta V_{24\text{h}} \ge 30\text{ kts}$).

Every feature is grounded in established tropical cyclone meteorology (e.g. Gray 1968, Kaplan & DeMaria 2003, DeMaria et al. 2005) and derived strictly from international reanalysis products (ECMWF ERA5 and NOAA PSL OISST v2.0).

---

## 2. Feature Registry Table

| Feature Name | Category | Units | Valid Range | Source Dataset | Missingness Protocol | Meteorological Role |
| :--- | :--- | :---: | :---: | :--- | :--- | :--- |
| `env_sst_celsius` | Oceanic | °C | $15.0 - 35.0$ | NOAA PSL OISST v2.0 | `NaN` if landlocked; `env_sst_is_observed=0.0` | Ocean thermal energy driving convective engine |
| `env_sst_potential_above_26c` | Oceanic | °C | $0.0 - 10.0$ | NOAA PSL OISST v2.0 | `NaN` if unobserved; `env_sst_is_observed=0.0` | Energy excess beyond the Palmén 1948 threshold |
| `env_sst_is_observed` | Indicator | Flag | $0.0\text{ or }1.0$ | CycloneGuard Protocol | Exact binary flag | Prevents synthetic zero-filling over land |
| `env_vws_magnitude_kts` | Dynamical | kts | $0.0 - 120.0$ | ECMWF ERA5 | `NaN` if unobserved; `env_vws_is_observed=0.0` | Deep-layer shear disrupting warm core |
| `env_vws_direction_deg` | Dynamical | deg | $0.0 - 360.0$ | ECMWF ERA5 | `NaN` if unobserved; `env_vws_is_observed=0.0` | Heading of shear vector / convective tilt azimuth |
| `env_wind_speed_850hpa_kts` | Dynamical | kts | $0.0 - 80.0$ | ECMWF ERA5 | `NaN` if unobserved; `env_vws_is_observed=0.0` | Low-level environmental steering/inflow |
| `env_wind_speed_200hpa_kts` | Dynamical | kts | $0.0 - 150.0$ | ECMWF ERA5 | `NaN` if unobserved; `env_vws_is_observed=0.0` | Upper-level outflow / jet stream interaction |
| `env_vws_delta_6h_kts` | Tendency | kts | $-50.0 - +50.0$ | ECMWF ERA5 | `NaN` if prior fix missing | 6-hour rate-of-change in shear environment |
| `env_vws_is_observed` | Indicator | Flag | $0.0\text{ or }1.0$ | CycloneGuard Protocol | Exact binary flag | Signals valid ERA5 wind vector matching |
| `env_relative_humidity_700hpa` | Moisture | % | $0.0 - 100.0$ | ECMWF ERA5 | `NaN` if unobserved; `env_rh_is_observed=0.0` | Mid-level humidity buffering against dry air entrainment |
| `env_relative_humidity_500hpa` | Moisture | % | $0.0 - 100.0$ | ECMWF ERA5 | `NaN` if unobserved | High-level humidity supporting convective buoyancy |
| `env_rh_is_observed` | Indicator | Flag | $0.0\text{ or }1.0$ | CycloneGuard Protocol | Exact binary flag | Signals valid ERA5 moisture matching |
| `env_dt_minutes` | Quality | min | $\le 60.0$ | CycloneGuard Protocol | Continuous minute offset | Temporal difference between fix and environmental grid |

---

## 3. Detailed Scientific Profiles by Feature

### 1. `env_vws_magnitude_kts`
- **Definition:** Magnitude of vector difference between horizontal wind vectors at $200\text{ hPa}$ and $850\text{ hPa}$:
  $$VWS = \frac{\sqrt{(u_{200} - u_{850})^2 + (v_{200} - v_{850})^2}}{1.852}$$
- **Source:** ECMWF ERA5 Reanalysis (1-hourly grid, $0.25^\circ$).
- **Spatial Alignment:** Exact IBTrACS latitude and longitude at time $t_0$.
- **Temporal Alignment:** Closest ERA5 synoptic hour (typically $\Delta t = 0.0\text{ minutes}$).
- **Missingness Behavior:** If ERA5 winds are unavailable, value is `np.nan` and `env_vws_is_observed = 0.0`. Imputed using training-partition median only during model training.
- **Leakage Safeguards:** Derived strictly at time $t_0$; no future winds from $t_0 + 6\text{h}$ or $t_0 + 24\text{h}$ are used.

### 2. `env_sst_celsius`
- **Definition:** Daily average sea surface temperature at cyclone center.
- **Source:** NOAA PSL High-Resolution Optimum Interpolation Sea Surface Temperature (OISST v2.0 highres, $0.25^\circ$ grid).
- **Spatial Alignment:** Center coordinate mapped to nearest $0.25^\circ$ ocean grid cell:
  $$\text{lat\_idx} = \text{round}\left(\frac{\text{lat} - (-89.875)}{0.25}\right), \quad \text{lon\_idx} = \text{round}\left(\frac{(\text{lon} \pmod{360}) - 0.125}{0.25}\right)$$
- **Missingness Behavior:** Land cells have physical fill values ($-9.969 \times 10^{36}$); mapped cleanly to `np.nan` with `env_sst_is_observed = 0.0`.
- **Leakage Safeguards:** OISST daily fields are indexed strictly for the observation day; no lookahead.

### 3. `env_vws_delta_6h_kts`
- **Definition:** Antecedent 6-hour change in vertical wind shear:
  $$\Delta VWS_{6\text{h}} = VWS(t_0) - VWS(t_0 - 6\text{h})$$
- **Physical Interpretation:** A storm moving into a rapidly relaxing shear environment ($\Delta VWS < 0$) is primed for core reorganization and rapid intensification.
- **Leakage Safeguards:** Uses exclusively past shear ($t_0 - 6\text{h}$); strictly prohibited from looking forward.

---

## 4. Feature Ablation Group Mappings

In Phase 10 model ablation experiments, features are clustered into 3 distinct functional groups:

- **Group E1 (Oceanic Thermal Potential):** `env_sst_celsius`, `env_sst_potential_above_26c`, `env_sst_is_observed`
- **Group E2 (Dynamical Wind Shear):** `env_vws_magnitude_kts`, `env_vws_direction_deg`, `env_wind_speed_850hpa_kts`, `env_wind_speed_200hpa_kts`, `env_vws_delta_6h_kts`, `env_vws_is_observed`
- **Group E3 (Mid-Tropospheric Moisture & Alignment):** `env_relative_humidity_700hpa`, `env_relative_humidity_500hpa`, `env_rh_is_observed`, `env_dt_minutes`
- **Group E_ALL (All Environmental Features):** All 13 features combined.
