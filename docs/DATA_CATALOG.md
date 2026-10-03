# CycloneGuard — Data Catalog & Provenance Registry

**Document Version:** 1.0.0  
**Phase:** Sprint 4 — Multi-Source Satellite Data Architecture & Ingestion  
**Verification Standard:** Strict Empirical Verification (No Guesses / No Fabrications)  

---

## 1. Registry Summary

The table below summarizes the verified status of all prospective data sources assessed for CycloneGuard:

| Source Identifier | Dataset Name | Agency / Provider | Data Type | Primary Format | Coverage | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `noaa_ibtracs` | International Best Track Archive for Climate Stewardship (v04r01) | NOAA NCEI | Cyclone Best-Tracks | CSV (174 columns) / NetCDF | Global (1848 – Present) | **`CONNECTED`** |
| `noaa_hursat_b1` | Hurricane Satellite Data (HURSAT-B1) | NOAA NCEI | Gridded Satellite IR/VIS | NetCDF-3 Classic | Global TC Center Crops (1978 – Present) | **`CONNECTED`** |
| `noaa_adt_hursat` | Advanced Dvorak Technique Reanalysis | NOAA NCEI / CIMSS | Objective Intensity Proxy | NetCDF / ASCII | Global TC Center Points (1978 – 2020) | **`AVAILABLE FOR DOWNLOAD`** |
| `isro_insat3d_mosdac` | INSAT-3D & 3DR Imager Radiances | ISRO / SAC (MOSDAC) | Full-Disk Geostationary Radiances | Hierarchical Data Format (HDF5) | North Indian Ocean ($40^\circ\text{E} - 120^\circ\text{E}$) | **`NOT YET INTEGRATED`** |
| `eumetsat_ascat` | Advanced Scatterometer Surface Wind Vectors | EUMETSAT / CMEMS | Ocean Vector Wind Fields | NetCDF-4 | Polar Swaths ($12.5\,\text{km}$ / $25\,\text{km}$) | **`OPTIONAL`** |
| `gpm_gmi_microwave` | GPM Microwave Imager (GMI) Radiances | NASA GES DISC / JAXA | Passive Microwave Eyewall Profiles | HDF5 / NetCDF-4 | Polar Orbiting Swath ($885\,\text{km}$) | **`OPTIONAL`** |

---

## 2. In-Depth Dataset Specifications

### 2.1 NOAA IBTrACS v04r01 (`noaa_ibtracs`)

* **Provider:** NOAA National Centers for Environmental Information (NCEI)
* **Purpose:** Official historical ground-truth reference for tropical cyclone track coordinates, minimum central pressures, maximum sustained winds, and intensity classifications.
* **Storage Format:** Standardized CSV with two-line header metadata (Row 0: column variable names; Row 1: physical units).
* **Key Variables Verified:**
  * `SID`: Unique Storm Identifier (13-character string, e.g., `2023130N05093`)
  * `SEASON`: 4-digit cyclone year
  * `NAME`: Official designated storm name
  * `BASIN`: Ocean basin code (`NI` for North Indian Ocean, `SI`, `WP`, `EP`, `NA`, `SP`, `SA`)
  * `SUBBASIN`: Sub-basin identifier (`BB` for Bay of Bengal, `AS` for Arabian Sea)
  * `ISO_TIME`: UTC observation timestamp (`YYYY-MM-DD HH:MM:SS`)
  * `LAT`, `LON`: Geographic center coordinate in decimal degrees north/east
  * `WMO_WIND`, `WMO_PRES`: World Meteorological Organization standardized intensity metrics
  * Regional agency fields: `NEWDELHI_WIND`, `NEWDELHI_PRES`, `NEWDELHI_GRADE` (India Meteorological Department RSMC New Delhi)
* **Temporal Resolution:** Synoptic 3-hourly and 6-hourly reporting intervals ($00, 03, 06, 09, 12, 15, 18, 21\,\text{UTC}$).
* **Spatial Resolution:** Point observation coordinates (precision: $0.1^\circ$ geographic).
* **Access Protocol:** Direct open HTTPS download from NCEI public repository (`https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/`).
* **Verified Status:** `CONNECTED`. Sample dataset `data/samples/ibtracs_sample_ni.csv` downloaded and validated (400 records across 10 storms).
* **Known Limitations:**
  * Different RSMC regional bodies enforce different wind averaging periods (IMD uses 3-minute sustained wind; JTWC uses 1-minute; WMO standard is 10-minute). CycloneGuard normalizer retains both WMO standard and IMD agency-reported fields.
  * Historical depressions and deep depressions occasionally lack central pressure estimates in raw archives.

---

### 2.2 NOAA HURSAT-B1 (`noaa_hursat_b1`)

* **Provider:** NOAA NCEI
* **Purpose:** High-resolution storm-centered geostationary infrared window and water vapor satellite imagery for spatial pattern analysis and feature extraction.
* **Storage Format:** NetCDF-3 Classic (`CDF-1`), conforming to Climate and Forecast (CF-1.6) metadata conventions.
* **Key Variables Verified:**
  * `IRWIN`: Infrared Window Channel (~11 µm calibrated brightness temperature, units: Kelvin)
  * `IRWVP`: Infrared Water Vapor Channel (~6.7 µm brightness temperature, units: Kelvin)
  * `VSCHN`: Visible Channel (daytime albedo fraction, units: dimensionless $0.0 - 1.0$)
  * `lat`, `lon`: 2D spatial coordinate arrays centered on best-track storm position
  * `time`: Seconds since 1970-01-01 00:00:00 UTC
* **Temporal Resolution:** 3-hourly synoptic intervals aligned with best-track records.
* **Spatial Resolution:** $301 \times 301$ regular spatial grid at $0.07^\circ$ (~8 km) nadir ground sampling distance.
* **Access Protocol:** Open NOAA NCEI HTTPS archive (`https://www.ncei.noaa.gov/data/hurricane-satellite-data/access/hursat-b1/v06/`).
* **Verified Status:** `CONNECTED`. Inspected and validated using pure-Python NetCDF-3 IO engine (`data/samples/hursat_b1_sample_mocha.nc`).
* **Known Limitations:**
  * Geostationary satellite sensor drift across generational platforms (Meteosat-5/7 vs. GMS/MTSAT vs. INSAT).
  * Extreme convective eyewall cloud tops can reach brightness temperatures $<180\,\text{K}$, requiring scale-factor preservation during integer packing.
  * Visible imagery is unavailable during nocturnal passes.

---

### 2.3 NOAA ADT-HURSAT (`noaa_adt_hursat`)

* **Provider:** NOAA NCEI / University of Wisconsin Cooperative Institute for Meteorological Satellite Studies (CIMSS)
* **Purpose:** Historical objective intensity reanalysis based on the automated Advanced Dvorak Technique.
* **Storage Format:** NetCDF-4 / Structured ASCII records.
* **Key Variables Verified:**
  * `raw_T_number`: Unconstrained empirical Dvorak cloud pattern score ($1.0 - 8.0$)
  * `final_T_number`: Time-constrained Dvorak score
  * `CI_number`: Current Intensity number
  * `central_pressure_mb`: ADT algorithmically estimated minimum central pressure (mb / hPa)
  * `max_wind_speed_kts`: ADT algorithmically estimated 1-minute sustained wind speed (knots)
  * `eyewall_scene_type`: Categorical scene classification (Pinhole Eye, Large Eye, Embedded Center, Curved Band, Shear)
* **Temporal Resolution:** Synchronous with HURSAT-B1 passes (3-hourly).
* **Access Protocol:** Public NOAA NCEI open archive (`https://www.ncei.noaa.gov/data/hurricane-satellite-data/access/adt-hursat/`).
* **Verified Status:** `AVAILABLE FOR DOWNLOAD`. Adapter implemented ([`ml/data/adapters/adt.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/data/adapters/adt.py)).
* **Scientific Rule Compliance:**
  * **Critical:** ADT values are algorithmic proxy models derived from satellite IR imagery, NOT physical in-situ measurements (dropsondes or flight-level reconnaissance). In CycloneGuard, ADT values are flagged as `DATA_TYPE = PROXY_ESTIMATE` and never treated as ground-truth observations.

---

### 2.4 ISRO INSAT-3D & 3DR Imager (`isro_insat3d_mosdac`)

* **Provider:** Indian Space Research Organisation (ISRO) / Space Applications Centre (SAC)
* **Data Portal:** Meteorological and Oceanographic Satellite Data Archival Centre (MOSDAC) — [https://www.mosdac.gov.in/](https://www.mosdac.gov.in/)
* **Purpose:** Operational high-frequency multi-spectral geostationary imagery over the Bay of Bengal and Arabian Sea.
* **Storage Format:** Hierarchical Data Format 5 (`.h5`).
* **Key Spectral Channels:**
  * Visible (VIS): $0.55 - 0.75\,\mu\text{m}$ ($1\,\text{km}$ nadir)
  * Shortwave Infrared (SWIR): $1.55 - 1.70\,\mu\text{m}$ ($1\,\text{km}$)
  * Middle Infrared (MIR): $3.80 - 4.00\,\mu\text{m}$ ($4\,\text{km}$)
  * Water Vapor (WV): $6.50 - 7.10\,\mu\text{m}$ ($8\,\text{km}$)
  * Thermal Infrared-1 (TIR-1): $10.30 - 11.30\,\mu\text{m}$ ($4\,\text{km}$) — primary cyclone eye tracking channel
  * Thermal Infrared-2 (TIR-2): $11.50 - 12.50\,\mu\text{m}$ ($4\,\text{km}$)
* **Temporal Resolution:** 30 minutes per satellite (15 minutes combined staggered constellation).
* **Spatial Coverage:** Full-disk geostationary coverage ($40^\circ\text{E} - 120^\circ\text{E}$, $45^\circ\text{S} - 45^\circ\text{N}$).
* **Verified Status:** `NOT YET INTEGRATED`. Detailed report published in [`docs/INSAT_DATA_STATUS.md`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/docs/INSAT_DATA_STATUS.md).
* **Known Limitations:**
  * Anonymous download prohibited; requires authenticated account, session token, and client API key.
  * Public accounts have a mandatory 3-day hold on Level-1 calibrated radiances.
  * Conversion from raw digital counts to physical brightness temperature requires application of sensor-specific pre-launch and on-orbit Planck lookup coefficients.

---

### 2.5 EUMETSAT ASCAT Ocean Surface Vector Winds (`eumetsat_ascat`)

* **Provider:** EUMETSAT / Copernicus Marine Environment Monitoring Service (CMEMS) / NOAA STAR
* **Purpose:** Calibrated near-surface 10-meter ocean vector wind speeds and wind directions for validating outer wind radii (e.g., R34, R50, R64 isotachs).
* **Storage Format:** NetCDF-4 Classic.
* **Key Variables:** `wind_speed` (m/s), `wind_dir` (degrees clockwise from north), `wind_stress`, `bsrn_rain_flag`.
* **Spatial Resolution:** Two $550\,\text{km}$ ground swaths separated by a $700\,\text{km}$ nadir blind spot at $12.5\,\text{km}$ and $25\,\text{km}$ grid resolution.
* **Verified Status:** `OPTIONAL`. Adapter implemented ([`ml/data/adapters/scatterometer.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/data/adapters/scatterometer.py)).
* **Known Limitations:**
  * Polar-orbiting satellite with 12–24 hour revisit cycle; often misses storm eyewalls due to the nadir swath gap.
  * C-band active microwave radar backscatter saturates at hurricane-force winds ($>65\,\text{kts}$) and suffers rain attenuation in the eyewall.

---

### 2.6 NASA/JAXA GPM Microwave Imager (`gpm_gmi_microwave`)

* **Provider:** NASA Goddard Earth Sciences Data and Information Services Center (GES DISC) / JAXA
* **Purpose:** Deep convective inner-core imaging to diagnose concentric eyewall cycles and precipitation rates through cloud canopies.
* **Storage Format:** HDF5 / NetCDF-4.
* **Key Channels:** 13 channels ($10.65\,\text{GHz}$ to $183.31\,\text{GHz}$) horizontal and vertical polarization.
* **Spatial Resolution:** $885\,\text{km}$ swath width with $5\,\text{km}$ nadir footprint at high frequencies ($89\,\text{GHz}$).
* **Verified Status:** `OPTIONAL`. Adapter implemented ([`ml/data/adapters/microwave.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/data/adapters/microwave.py)).
* **Known Limitations:**
  * Infrequent overpasses (1 to 2 passes per 24 hours per storm center).
  * Requires active NASA Earthdata Login credentials for API streaming.
