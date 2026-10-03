# Sprint 8 Final Report — Historical HURSAT-B1 Acquisition, Coincidence Matching & Dataset Expansion

**Sprint:** 8 — Historical Satellite Data Acquisition, IBTrACS Matching, Patch Extraction, Dataset Versioning & Quality Control  
**Status:** Completed & Grounded in Real Observational Evidence  
**Date:** 2026-09-27  
**Dataset Version:** `cycloneguard-satellite-hursat-v2`  
**Previous Dataset Version:** `cycloneguard-satellite-v1` (Preserved intact)  
**Model Training Status:** **None** (Strictly forbidden in Sprint 8; no CNNs, ViTs, or multimodal networks trained)

---

## 1. Historical Storms Targeted

A bounded historical inventory of North Indian Ocean (NI) tropical cyclones was constructed using the verified IBTrACS database, adhering to strict scientific criteria:
1. Valid, continuous synoptic best-track tracks.
2. Temporal coverage within NOAA HURSAT-B1 v06 archive availability (1978–2016).
3. Usable timestamps and center coordinates.
4. Sufficient intensity observations for forward 24-hour Rapid Intensification (RI) ground truth labeling.
5. Representation across multiple seasons and subbasins (Bay of Bengal and Arabian Sea).

A targeted set of **6 historical North Indian Ocean cyclones** was cataloged in [`data/manifests/historical_target_storms.json`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/data/manifests/historical_target_storms.json):

| Storm ID | Storm Name | Season | Basin / Subbasin | Track Observations | Vmax Peak (kts) | Lifecycle Window (UTC) |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| `2013281N12098` | **PHAILIN** | 2013 | NI / BB | 55 | 115.0 | 2013-10-07 12:00 to 2013-10-14 06:00 |
| `2013322N13090` | **HELEN** | 2013 | NI / BB | 43 | 55.0 | 2013-11-18 00:00 to 2013-11-23 06:00 |
| `2014279N11096` | **HUDHUD** | 2014 | NI / BB | 66 | 95.0 | 2014-10-06 06:00 to 2014-10-14 09:00 |
| `2014297N11062` | **NILOFAR** | 2014 | NI / AS | 73 | 110.0 | 2014-10-24 18:00 to 2014-10-31 18:00 |
| `2015301N11065` | **CHAPALA** | 2015 | NI / AS | 61 | 115.0 | 2015-10-28 00:00 to 2015-11-04 12:00 |
| `2015309N14067` | **MEGH** | 2015 | NI / AS | 49 | 95.0 | 2015-11-04 18:00 to 2015-11-10 18:00 |
| **Total** | **6 Storms** | **3 Seasons** | **2 Subbasins** | **347** | — | **2013–2015** |

---

## 2. Historical Storms Acquired

All **6 target historical storms** were acquired without omitting or dropping any target cyclone. The acquisition pipeline successfully retrieved the full multi-day storm lifecycle archives from NOAA NCEI for every targeted storm.

- **Targeted Storms:** 6
- **Acquired Storms:** 6 (100.0% completion)
- **Geographic Representation:** 3 Bay of Bengal storms (Phailin, Helen, Hudhud) + 3 Arabian Sea storms (Nilofar, Chapala, Megh).

---

## 3. HURSAT Assets Discovered

Before initiating any downloads, the archive discovery engine systematically audited the NOAA NCEI HURSAT-B1 v06 repository across candidate historical seasons (2013, 2014, 2015).
- **Discovered Archive Assets:** **287** unique storm tarball archives logged in [`data/manifests/hursat_archive_inventory.jsonl`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/data/manifests/hursat_archive_inventory.jsonl).
- **Candidate Years Audited:** 2013 (95 storms), 2014 (98 storms), 2015 (94 storms).
- **Discovery Method:** HTTP inventory inspection verifying remote URI, file size via HTTP HEAD, and storm identity mapping. Zero blind scraping.

---

## 4. Assets Downloaded

The download process executed via `ResilientDownloader` within configured resource ceilings (max download budget 250 MB, max file size 60 MB):
- **Archive Tarballs Downloaded / Cached:** **6** tarball archives (167,272,323 bytes total / ~167.3 MB).
- **Extracted NetCDF Granules:** **887** calibrated NetCDF-3/NetCDF-4 files unpacked into `data/raw/hursat/{storm_id}/`.
- **Download Status:** 100% successful (6/6 archives verified via SHA-256 checksums; 0 corruptions, 0 retries exhausted).
- **Download Report:** Logged at [`data/reports/hursat_download_report.json`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/data/reports/hursat_download_report.json).

---

## 5. Assets Validated

Every downloaded NetCDF file was subjected to strict structural and physical validation via [`HURSATSourceValidator`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/data/validation/source_validators/hursat_validator.py):
- **Total Validated NetCDF Files:** **887**
- **Structurally Valid Files:** **887** (100.0%)
- **Corrupted / Truncated Files:** **0** (0.0%)
- **Files with Missing Coordinates:** **0** (0.0%)
- **Channels Verified:** Clean IR Window (`IRWIN`), Water Vapor (`IRWVP`), and Visible (`VSCHN`).
- **Physical Ranges Audited:** Brightness temperatures verified within physical boundaries ($160.0\,\text{K} \le T_b \le 340.0\,\text{K}$).
- **Validation Report:** Logged at [`data/reports/hursat_validation_report.json`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/data/reports/hursat_validation_report.json).

---

## 6. Track-Satellite Matches

Using the existing `CoincidenceEngine` with an explicit temporal tolerance of $\pm 30.0$ minutes (geostationary IR standard) and spatial domain bounds:
- **Total IBTrACS Track Points Targeted:** **347**
- **Coincident Matches Found:** **347** (100.0% match rate)
- **Mean Temporal Delta:** **0.0 minutes** (all 347 track points align directly with 3-hourly geostationary scan schedules).
- **Max Temporal Delta:** 0.0 minutes (within $\pm 30.0$ min boundary).
- **Spatial Bounds Status:** 347 / 347 cyclone centers fall completely within satellite grid bounds.
- **Coincidence Table:** Recorded in [`data/processed/hursat_coincidence_table.csv`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/data/processed/hursat_coincidence_table.csv).

---

## 7. Valid Patches

Cyclone-centered spatial patches were extracted using [`CyclonePatchExtractor`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/data/preprocessing/patch_extractor.py), centering pixel [32, 32] on the cyclone center:
- **Total Extracted Patches:** **1,020** physical patches saved in [`data/processed/satellite_patches/`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/data/processed/satellite_patches/).
  - **`IRWIN` (10.8 µm Clean Window IR):** 347 patches (100.0%)
  - **`IRWVP` (6.7 µm Upper Tropospheric Water Vapor):** 347 patches (100.0%)
  - **`VSCHN` (0.6 µm Visible Albedo):** 326 patches (93.9%; nighttime passes correctly omitted)
- **Patch Format:** $64 \times 64$ `float32` arrays preserving raw physical units (Kelvin for IR/WV, albedo reflectance fraction for VIS).
- **Destructive Compression:** **Zero** (no 8-bit quantization, no JPEG compression, no screenshot artifacts).
- **Quality Distribution:** 969 Nominal, 51 Edge Padded, 0 Excessive NaNs (> 50%).

---

## 8. RI-Labeled Patches

Following the Kaplan & DeMaria (2003) / WMO Rapid Intensification definition ($\Delta V_{24\text{h}} \ge 30\,\text{kts}$ over $H = 24.0\,\text{h} \pm 3.0\,\text{h}$):
- **Total Historical Coincident Fixes:** 347
- **Supervised Instances ($t+24$h future track available):** **299**
- **Unsupervised / End-of-Track Instances:** **48** (cyclolysis / post-tropical transition within 24h)
- **RI-Positive Samples ($\Delta V_{24\text{h}} \ge 30\,\text{kts}$):** **39** (13.04%)
- **RI-Negative Samples ($\Delta V_{24\text{h}} < 30\,\text{kts}$):** **260** (86.96%)
- **Labeled Dataset Artifact:** [`data/processed/hursat_ri_samples.csv`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/data/processed/hursat_ri_samples.csv).

---

## 9. Train / Validation / Test Counts

A strict storm-wise partition was configured in [`ml/config/historical_split_config.json`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/config/historical_split_config.json) to isolate complete cyclone lifecycles:

| Partition | Assigned Storms | Total Fixes | Supervised Samples ($N$) | RI-Positive ($N$) | RI-Negative ($N$) | RI Prevalence |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **TRAIN** | PHAILIN, HELEN, HUDHUD, NILOFAR | 237 | 204 | 23 | 181 | 11.27% |
| **VAL** | MEGH | 49 | 42 | 6 | 36 | 14.29% |
| **TEST** | CHAPALA | 61 | 53 | 10 | 43 | 18.87% |
| **Total** | **6 Storms** | **347** | **299** | **39** | **260** | **13.04%** |

---

## 10. RI Prevalence Across Partitions

In Sprint 7, coincident observations were limited to a single storm with 0 training-set satellite instances and 0 validation RI events.  
In Sprint 8:
- **Training Set RI Prevalence:** **11.27%** (23 / 204)
- **Validation Set RI Prevalence:** **14.29%** (6 / 42) — **Validation now contains non-zero RI events!**
- **Testing Set RI Prevalence:** **18.87%** (10 / 53) — **Held-out test set contains non-zero RI events!**
- **Overall Dataset Prevalence:** **13.04%** (39 / 299)

Both evaluation partitions now possess genuine Rapid Intensification events, resolving the zero-positive evaluation dilemma from prior sprints.

---

## 11. Leakage Audit

A comprehensive 7-point data leakage audit was executed by [`SatelliteLeakageAuditor`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/data/validation/leakage_audit.py), with results published in [`docs/SPRINT8_LEAKAGE_AUDIT.md`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/docs/SPRINT8_LEAKAGE_AUDIT.md):

1. **Same storm across partitions:** **0 overlap** ($\text{Train} \cap \text{Val} = \emptyset$, $\text{Train} \cap \text{Test} = \emptyset$, $\text{Val} \cap \text{Test} = \emptyset$).
2. **Duplicate satellite asset across partitions:** **0 shared assets** across train/val/test.
3. **Duplicate patch across partitions:** **0 shared patches** across train/val/test.
4. **Future imagery relative to target:** **0 violations** ($\Delta t \le 30.0$ min; mean $\Delta t = 0.0$ min).
5. **Future track information entering features:** **0 violations** (features contain only synchronous state at $t$).
6. **Target generation contamination:** **Verified independent** (target derived strictly from forward IBTrACS wind speed changes; satellite pixels do not inform target).
7. **Multiple patches derived from same source file:** **0 cross-time asset reuse** (each patch corresponds to a distinct observation fix).

**Audit Verdict:** **PASSED (All 7 leakage firewalls verified with zero violations).**

---

## 12. Dataset Versioning

A new immutable dataset version was created:
- **Version ID:** `satellite_hursat_v2` (Software identifier: `cycloneguard-satellite-hursat-v2`).
- **Location:** [`data/datasets/satellite_hursat_v2/`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/data/datasets/satellite_hursat_v2/).
- **Artifacts Bundled:**
  - `metadata.json`: Full provenance, channels, resolutions, split maps, and quality criteria.
  - `dataset_manifest.json`: List of all 347 coincident records and 1,020 patch files.
  - `coincidence_table.csv`: Synchronous track-to-satellite alignment table.
  - `ri_samples.csv`: Formatted 24h RI-labeled supervised dataset.
- **Immutability:** Existing version `satellite_v1` was preserved completely untouched.

---

## 13. Storage Footprint

The pipeline executed with strict disk budget discipline:
- **Raw Tarball Archives:** ~167.3 MB (`data/raw/hursat/*.tar.gz`)
- **Unpacked NetCDF Granules:** ~221.0 MB (`data/raw/hursat/{storm_id}/*.nc`)
- **Extracted 64x64 float32 Patches:** ~16.5 MB (`data/processed/satellite_patches/`)
- **Processed Tables & Manifests:** ~1.2 MB
- **Total Sprint 8 Storage Incurred:** **~406 MB** (well below the disk ceiling).

---

## 14. Failures & Anomalies

- **Network Failures:** 0 download errors or HTTP dropouts.
- **Corrupt Granules:** 0 corrupt NetCDF files out of 887.
- **Missing Synchronous Imagery:** 0 (all 347 target fixes had coincident HURSAT files within $\pm 30$ min).
- **Missing Visible Imagery:** 21 nighttime fixes correctly flagged as missing visible channel (`VSCHN`), while retaining infrared (`IRWIN`) and water vapor (`IRWVP`).

---

## 15. Data-Access Limitations

1. **HURSAT-B1 Archive Horizon:** NOAA HURSAT-B1 v06 concludes in **2016**. Consequently, storms from 2017 to the present (including Cyclone Fani 2019, Amphan 2020, Mocha 2023) cannot be sourced from this archive.
2. **Modern Geostationary Imagers (INSAT-3D/3DR):** Operational ISRO imager data covering 2013–present requires authenticated credentials via the MOSDAC user portal, subject to a 3-day hold policy and individual researcher vetting.
3. **Polar Microwave & Scatterometer Scarcity:** Sensors such as GPM GMI and MetOp ASCAT provide only 1–2 overpasses per storm per day over the North Indian Ocean, resulting in 0 multimodal triples in this historical batch.

---

## 16. Dataset Readiness Classification

Based on empirical data counts ($N_{\text{valid\_patches}} = 1,020$, $N_{\text{unique\_storms}} = 6$, $N_{\text{supervised}} = 299$, $N_{\text{RI+}} = 39$), the dataset is formally classified as:

### **Classification B: Suitable for exploratory spatial baseline**

### Rationale:
- **Progress from Sprint 7:** Expanded the dataset from 1 coincident observation to 347 coincident observations (1,020 patches across 3 channels), providing 299 supervised samples and 39 confirmed RI events across both subbasins.
- **Why it supports Classification B:** It provides enough statistical support for **exploratory spatial baselines** — such as extracting engineered spatial features (radial brightness temperature profiles, core axisymmetric convective intensity, cloud-top temperature gradients, azimuthal wavenumber asymmetries) and training classical classifiers (Ridge, Logistic Regression, Random Forest).
- **Why it is NOT Classification C or D:** A dataset with only **4 training storms** (204 training samples) cannot provide sufficient meteorological diversity to train deep Convolutional Neural Networks (CNNs) or Vision Transformers (ViTs) from scratch without catastrophic storm-level memorization and spatial overfitting.

---

## 17. Exact Next Bottleneck

The immediate bottleneck to scaling beyond exploratory baselines is **storm cohort sample size**:
1. To advance to **Classification C (Small CNN experiment)**, the pipeline must expand historical acquisition across the broader 1978–2016 HURSAT-B1 archive to reach at least **30–50 unique North Indian Ocean storms** (> 1,500 supervised samples).
2. To advance to **Classification D (Multimodal spatial-temporal modeling)**, modern operational access to authenticated ISRO INSAT-3D/3DR and GPM microwave radiometer archives must be unlocked to provide multi-sensor coincident observations.

---

## Summary of Empirical Milestones

| Metric | Sprint 7 Status | Sprint 8 Result | Absolute Increase |
| :--- | :---: | :---: | :---: |
| **Total Target Storms** | 1 (Mocha sample) | **6 Historical Storms** | +5 storms |
| **Total Track Fixes** | 400 (track only) | **347 (NI Historical)** | — |
| **Coincident Satellite Matches** | 1 (0.25%) | **347 (100.0%)** | **+346 matches** |
| **Extracted Spatial Patches** | 3 patches | **1,020 patches** | **+1,017 patches** |
| **Supervised RI Samples ($t+24$h)** | 0 (satellite coincident) | **299 samples** | **+299 samples** |
| **RI-Positive Events** | 0 (satellite coincident) | **39 RI+ events** | **+39 RI events** |
| **Validation Set RI Events** | 0 | **6 RI+ events** | **Confirmed positive balance** |
| **Test Set RI Events** | 0 | **10 RI+ events** | **Confirmed positive balance** |
| **Leakage Audit Violations** | 0 | **0 (7/7 passed)** | Zero tolerance preserved |
| **Dataset Version** | `satellite_v1` | **`satellite_hursat_v2`** | Staged & documented |
| **Dataset Scale Decision** | Classification A | **Classification B** | Readiness upgraded |
