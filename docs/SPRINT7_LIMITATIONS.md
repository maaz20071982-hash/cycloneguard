# Sprint 7 — Scientific & Data Architecture Limitations

**Document Version:** 1.0.0  
**Audit Date:** 2026-09-26  
**Status:** Grounded in Verified Observational Evidence (Zero Placeholders)  

---

## 1. Executive Summary

Sprint 7 established the necessary infrastructure for multi-source satellite acquisition, temporal/spatial coincidence matching, quality control, and cyclone-centered patch extraction.

However, in accordance with the strict scientific rules of CycloneGuard, **we do NOT claim that a multi-source dataset is complete**. The empirical coverage audit proves that coincident satellite data remains **critically sparse** in the current staged environment.

---

## 2. Inaccessible & Pending Observational Sources

### A. ISRO MOSDAC (INSAT-3D / INSAT-3DR / INSAT-3DS)
- **Status:** **`DOCUMENTED`** (0 local observations).
- **Inaccessibility Cause:** Anonymous programmatic bulk download is prohibited by ISRO MOSDAC security architecture. Access requires verified user accounts, manual session handshakes, and individual API tokens.
- **Latency Restrictions:** Standard non-operational accounts are subject to a **3-day data hold** for Level-1 products, preventing automated real-time retrieval without specialized operational clearances.
- **Impact:** The highest-resolution regional geostationary sensor for the North Indian Ocean cannot be automatically downloaded without individual user credentials.

### B. NASA GES DISC (GPM Microwave Imager - GMI)
- **Status:** **`AVAILABLE ONLINE`** (0 local observations).
- **Inaccessibility Cause:** Programmatic downloads require authenticated NASA Earthdata Login credentials (`.netrc` authentication).
- **Temporal Gaps:** GPM is a polar-orbiting constellation with a non-geostationary orbit. Overpasses occur approximately 1–2 times every 24 hours over a specific tropical cyclone. Even with automated downloads, passive microwave observations are fundamentally intermittent and cannot provide uniform 3-hourly cadence.

### C. EUMETSAT Metop ASCAT Scatterometer
- **Status:** **`AVAILABLE ONLINE`** (0 local observations).
- **Inaccessibility Cause:** Direct programmatic access to the EUMETSAT Data Store requires consumer keys and client secrets. Historical subsets are partially mirrorable via NOAA CoastWatch ERDDAP.
- **Observation Sparsity:** Polar scatterometer swaths have narrow footprints (~1,000 km) and sub-daily revisit rates, resulting in substantial spatial and temporal gaps between storm track fixes and swath coverage.

---

## 3. Historical Coverage Gaps in HURSAT-B1

### A. Archive End Date (1978–2016 vs 2023 Season)
- The official NOAA NCEI HURSAT-B1 v06 archive ends in **2016**.
- The 10 ground-truth tropical cyclones in our verified IBTrACS sample occurred during the **2023 season**.
- Consequently, while HURSAT-B1 provides decades of historical cases (e.g. Cyclone Phailin 2013, Hudhud 2014), the 2023 season only contains the single verified benchmark fixture (`data/samples/hursat_b1_sample_mocha.nc` for Cyclone Mocha at `2023-05-12T06:00:00Z`).
- **Empirical Coverage:** **1 out of 400 track fixes** (0.25% coverage).

---

## 4. Disparate Spatial Resolutions & Projections

| Sensor | Native Projection | Native Resolution | Standardized Grid Resolution | Spatial Artifact Risk |
| :--- | :--- | :---: | :---: | :--- |
| **HURSAT-B1** | Equirectangular (Lat/Lon) | ~8 km (0.08°) | 0.08° (64x64 patch) | Low distortion; nearest-neighbor interpolation used. |
| **INSAT-3D** | Geostationary (Fixed Grid) | 4 km (TIR), 8 km (WV) | 0.08° (Resampling required) | Parallax shift near disk edge (high latitudes/longitudes). |
| **GPM GMI** | Orbital Conical Swath | 5 km (89 GHz) to 25 km (10 GHz) | Swath-to-grid reprojection required | Channel foot-print mismatch (10 GHz sees broad rain; 89 GHz sees tight ice cores). |
| **ASCAT** | Swath Along/Cross-Track | 12.5 km / 25 km | Wind vector gridding required | Rain contamination flags can invalidate high-wind retrievals. |

---

## 5. Sensor-Specific Physical Artifacts

1. **Cirrus Cloud Obscuration:**
   - Geostationary infrared channels (IRWIN ~10.8 µm) measure cloud-top brightness temperature. Thick cirrus canopies frequently obscure the low-level circulation center during early genesis, leading to false center estimates or masking rapid intensification signals.
2. **Limb Darkening & Water Vapor Attenuation:**
   - Satellite zenith angle variations across geostationary disks introduce optical path lengthening and atmospheric attenuation near the disk edge.
3. **Diurnal Solar Heating Variations:**
   - Shortwave visible (VSCHN) imagery is available exclusively during daylight hours, creating a 12-hour periodic void that neural networks must not exploit or fail on.

---

## 6. Preprocessing Assumptions

1. **Center Alignment:**
   - Patches are centered on the IBTrACS best-track interpolated center $(lat_c, lon_c)$. Best-track fixes have an inherent operational positioning uncertainty of $\sim 15-30$ km (Landsea & Franklin 2013).
2. **Nearest-Neighbor Resampling:**
   - Patch extraction uses nearest-neighbor mapping to preserve raw calibrated physical brightness temperatures (Kelvin) without artificial numerical smoothing.
3. **Boundary Padding:**
   - When a cyclone center is near the edge of the satellite composite, pixels beyond the grid boundary are padded with `NaN` and flagged with `BOUNDARY_PADDED`.

---

## 7. Operational Primacy & Disclaimer

- CycloneGuard is a research and decision-support architecture.
- Real-time tropical cyclone warnings, watches, and evacuation advisories for the North Indian Ocean basin are under the exclusive statutory authority of the **India Meteorological Department (IMD / RSMC New Delhi)**.
- Research models must never override official meteorological advisories.
