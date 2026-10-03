# Sprint 10 Environmental Data Sources Registry & Acquisition Specification

**Document Version:** 1.0  
**Phase:** Sprint 10 — Phase 2 Deliverable  
**Date:** 2026-09-27  

---

## 1. Overview & Research Scope

Sprint 10 investigates whether large-scale atmospheric and oceanic environmental conditions provide independent predictive information for tropical cyclone Rapid Intensification (RI, $\Delta V_{24\text{h}} \ge 30\text{ kts}$) when combined with temporal intensity kinematics (Model T) and satellite spatial proxies (Model S).

Under strict non-negotiable scientific rules:
1. **Zero Data Fabrication:** No synthetic, simulated, or pseudo-environmental values may be generated.
2. **Authoritative Sources Only:** Environmental data must originate from verified international meteorological and oceanographic reanalysis products.
3. **No Zero-Filling:** Unobserved or missing variables must be represented via explicit missingness flags and NaN values; zero-filling is strictly prohibited.
4. **Directional Causality ($t \le t_0$):** All environmental variables must correspond to the observation fix timestamp $t_0$ (or an antecedent window); no future information from $t_0 + 24\text{h}$ may be used.

---

## 2. Identified Environmental Data Sources

### Source 1: ECMWF ERA5 Atmospheric Reanalysis
- **Authoritative Provider:** European Centre for Medium-Range Weather Forecasts (ECMWF) / Copernicus Climate Change Service (C3S).
- **Dataset / Product:** ERA5 Reanalysis (5th generation ECMWF atmospheric reanalysis of global climate).
- **Access Route:** Open-Meteo Historical Weather Archive API (`https://archive-api.open-meteo.com/v1/archive`).
- **Temporal Resolution:** 1-hourly (sampled at exact cyclone fix time $t_0$).
- **Spatial Resolution:** $0.25^\circ \times 0.25^\circ$ regular lat/lon grid ($\approx 28\text{ km}$ at tropical latitudes).
- **Coverage Period:** 1940 to present (covers all historical storm seasons: 2013, 2014, 2015).
- **Licensing:** Open access under the Copernicus Products Licence / Creative Commons Attribution 4.0 International (CC BY 4.0).
- **Variables Retrieved:**
  1. `wind_speed_850hPa` (Lower-tropospheric wind speed, km/h or m/s)
  2. `wind_direction_850hPa` (Lower-tropospheric wind direction, degrees clockwise from north)
  3. `wind_speed_200hPa` (Upper-tropospheric wind speed, km/h or m/s)
  4. `wind_direction_200hPa` (Upper-tropospheric wind direction, degrees clockwise from north)
  5. `relative_humidity_700hPa` (Mid-tropospheric moisture, %)
  6. `surface_pressure` (Atmospheric boundary pressure, hPa)

### Source 2: Copernicus Marine / ECMWF ERA5 Ocean (Sea Surface Temperature)
- **Authoritative Provider:** Copernicus Marine Environment Monitoring Service (CMEMS) / ECMWF ERA5-Ocean.
- **Dataset / Product:** ERA5 Marine / CMEMS Global Ocean Physics Reanalysis.
- **Access Route:** Open-Meteo Marine Archive API (`https://marine-api.open-meteo.com/v1/marine`).
- **Temporal Resolution:** 1-hourly.
- **Spatial Resolution:** $0.25^\circ \times 0.25^\circ$ ocean grid.
- **Coverage Period:** 1940 to present.
- **Licensing:** Open access under Copernicus Marine Service license.
- **Variables Retrieved:**
  1. `sea_surface_temperature` (Ocean foundation / skin temperature, °C).

---

## 3. Physical Feature Definitions & Equations

### A. Deep-Layer Vertical Wind Shear (850–200 hPa)
Vertical wind shear is the vector difference between horizontal winds at $200\text{ hPa}$ (approx. $12\text{ km}$ altitude, outflow layer) and $850\text{ hPa}$ (approx. $1.5\text{ km}$ altitude, low-level steering/inflow layer).

1. **Horizontal Wind Decomposition:**
   For each pressure level $p \in \{850, 200\}$ with wind speed $S_p$ and meteorological direction $\theta_p$ (direction wind is blowing *from* in radians):
   $$u_p = -S_p \cdot \sin(\theta_p)$$
   $$v_p = -S_p \cdot \cos(\theta_p)$$

2. **Vector Shear Components:**
   $$u_{\text{shear}} = u_{200} - u_{850}$$
   $$v_{\text{shear}} = v_{200} - v_{850}$$

3. **Shear Magnitude:**
   $$VWS = \sqrt{u_{\text{shear}}^2 + v_{\text{shear}}^2}$$
   Converted to knots ($1\text{ km/h} \approx 0.539957\text{ kts}$).

4. **Shear Direction:**
   $$\theta_{\text{shear}} = \text{atan2}(-u_{\text{shear}}, -v_{\text{shear}}) \pmod{360^\circ}$$

5. **Physical Interpretation:**
   - **Low Shear ($< 15\text{ kts}$):** Favorable for vertical convective alignment, minimal ventilation of the warm core, high RI potential.
   - **Moderate Shear ($15 - 25\text{ kts}$):** Marginal; vortex tilting and asymmetrical convection.
   - **High Shear ($> 25\text{ kts}$):** Strong RI inhibition; severe core ventilation and dry air entrainment.

### B. Sea Surface Temperature (SST)
- **Variable:** `env_sst_celsius`
- **Units:** Degrees Celsius (°C).
- **Physical Interpretation:**
  - $SST < 26.0^\circ\text{C}$: Thermodynamically hostile to RI.
  - $26.5^\circ\text{C} \le SST < 28.5^\circ\text{C}$: Sufficient thermodynamic energy for tropical development.
  - $SST \ge 29.0^\circ\text{C}$: Extremely warm ocean pool; very high Maximum Potential Intensity (MPI).

### C. Mid-Tropospheric Relative Humidity (700 hPa)
- **Variable:** `env_relative_humidity_700hpa`
- **Units:** Percent (%).
- **Physical Interpretation:**
  - Low RH ($< 50\%$): Dry environmental air capable of eroding convective eyewalls through downdraft cooling.
  - High RH ($> 70\%$): Moist tropical environment insulating the cyclone vortex.

---

## 4. Landfall & Missing-Data Handling Protocol

1. **Ocean vs. Land Boundaries:**
   When a cyclone makes landfall or approaches complex coastlines (e.g. Phailin moving into Odisha, India, or Megh tracking into the Horn of Africa), marine grids produce `null` (None) for Sea Surface Temperature.
2. **Missingness Flagging:**
   - Every environmental feature is paired with an explicit binary indicator (e.g. `env_sst_is_observed`).
   - If a fix is over land, `env_sst_is_observed = 0.0` and `env_sst_celsius = np.nan`.
   - **Zero-filling is strictly prohibited**, because filling an unobserved SST with $0^\circ\text{C}$ would distort linear scalers and introduce pseudo-arctic temperatures into tropical cyclone models.
3. **Imputation Safeguards:**
   - Missing environmental values are imputed using median values computed **strictly on the training partition**.
