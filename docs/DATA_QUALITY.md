# CycloneGuard — Data Quality, Validation & Governance Standard

**Document Version:** 1.0.0  
**Phase:** Sprint 4 — Multi-Source Satellite Data Architecture & Ingestion  
**Status:** Mandatory Operational Rules  

---

## 1. The Twelve Immutable Scientific Data Rules

Every developer, automated pipeline script, and ML training routine in CycloneGuard must unconditionally adhere to the following 12 scientific rules:

1. **Never fabricate observations:** Zero synthetic or hallucinated satellite pixels or station measurements.
2. **Never fabricate cyclone tracks:** Positions and bearings must originate from verified WMO or national meteorological agency best-track records.
3. **Never fabricate intensity:** Minimum central pressure and maximum sustained wind speeds must reflect empirical records.
4. **Never fabricate satellite channels:** Only spectral bands physically sensed and calibrated on the host spacecraft may be loaded.
5. **Never assume units:** Units must be verified from header metadata before any numerical calculation (e.g., verifying whether wind speed is in $\text{knots}$, $\text{m/s}$, or $\text{km/h}$; verifying whether pressure is in $\text{mb}$, $\text{hPa}$, or $\text{Pa}$).
6. **Never assume variable names:** Inspect exact variable keys via CF-compliant netCDF/HDF5 or CSV tools before querying data arrays.
7. **Never assume temporal resolution:** Verify time intervals from sequence timestamps rather than assuming equidistant spacing.
8. **Never silently fill missing scientific values:** Missing pixels, missing soundings, or dropped telemetry must be represented as `NaN` or explicitly flagged; never replace missing values with arbitrary zeros, column averages, or random noise.
9. **Never mix storms across train/test sets:** All observations from a given cyclone must strictly reside within exactly one partition (`train`, `val`, or `test`). Data leakage invalidates meteorological evaluation.
10. **Never call a proxy ground truth without documenting it:** Algorithms like the Advanced Dvorak Technique (ADT) are empirical proxy models, not in-situ ground-truth measurements.
11. **Never claim a source is connected unless verified:** Any data provider requiring unverified credentials or manual intervention must be classified as `NOT YET INTEGRATED` or `AVAILABLE FOR DOWNLOAD`.
12. **Never claim real-time capability unless actually implemented:** Distinguish clearly between retrospective reanalysis data streams and verified operational near-real-time (NRT) feeds.

---

## 2. Validation Architecture (`DataValidator`)

Located in [`ml/data/validation/validator.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/data/validation/validator.py):

### 2.1 File & Header Integrity Checks
* **Physical File Verification:** Checks file existence, non-zero file size, and read permissions.
* **Magic Byte Inspection:** Confirms binary signatures (`CDF\x01` or `CDF\x02` for NetCDF-3, `\x89HDF\r\n\x1a\n` for HDF5).
* **Dimension Verification:** Ensures required spatial/temporal dimensions are present and positive.

### 2.2 Numerical & Coordinate Range Validation
* **Latitude Range:** Strictly enforced within $[-90.0^\circ, +90.0^\circ]$.
* **Longitude Range:** Strictly mapped and validated within $[-180.0^\circ, +180.0^\circ]$.
* **Brightness Temperatures:** Verified within physical terrestrial tropospheric bounds ($160.0\,\text{K} \le T_b \le 340.0\,\text{K}$). Values outside trigger `ERROR`.
* **Wind Speed Bounds:** Verified within $[0.0, 250.0]\,\text{knots}$.
* **Central Pressure Bounds:** Verified within $[850.0, 1050.0]\,\text{mb}$.

### 2.3 Temporal Monotonicity & Record Uniqueness
* **Strict Monotonicity:** Track points must advance in time ($t_{i+1} > t_i$). Reverse or non-chronological records trigger validation errors.
* **Duplicate Detection:** Pairs of $(SID, \text{ISO\_TIME})$ must be unique within an agency track series.

### 2.4 Structured Validation Envelope
The validator emits an immutable report with status levels:
* `VALID`: All checks passed with 100% compliance.
* `WARNING`: Minor non-critical anomalies detected (e.g., missing pressure values in early tropical disturbance phase) that do not corrupt spatial alignment.
* `ERROR`: Critical data corruption (e.g., corrupted file header, out-of-bounds geographic coordinate, unphysical temperatures) preventing scientific use.

---

## 3. Scientific Normalization Standard (`DataNormalizer`)

Located in [`ml/data/normalization/normalizer.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/data/normalization/normalizer.py):

| Dimension | Raw Variance Encountered | CycloneGuard Canonical Standard |
| :--- | :--- | :--- |
| **Timestamps** | UNIX epoch, JD, local time strings | UTC ISO-8601 formatted string (`YYYY-MM-DDTHH:MM:SSZ`) |
| **Longitude** | $0^\circ - 360^\circ$ East vs $-180^\circ - +180^\circ$ | Canonical $[-180.0^\circ, +180.0^\circ]$ |
| **Latitude** | Descending (North-to-South) or Ascending | Monotonically strictly verified $[-90.0^\circ, +90.0^\circ]$ |
| **Wind Speed** | Knots, m/s, km/h | Stored in Knots ($1\,\text{kt} = 0.514444\,\text{m/s}$); agency averaging periods explicitly preserved |
| **Pressure** | mb, hPa, Pa | Canonical Millibars / Hectopascals ($1\,\text{mb} = 1\,\text{hPa}$) |
| **Brightness Temp** | Unscaled 16-bit integer counts | Calibrated Physical Kelvin ($\text{K}$) via verified sensor scale/offset equations |
| **Missing Values** | `-999`, `-9999`, empty whitespace strings | Canonical IEEE 754 Floating-Point `NaN` |

---

## 4. Zero-Leakage Storm-Wise Partitioning Standard (`StormWiseSplitter`)

Located in [`ml/data/splitting/storm_split.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/data/splitting/storm_split.py):

### 4.1 The Meteorological Data Leakage Problem
In standard computer vision and time-series modeling, random record-level train/test splitting is fatal:
* Cyclone satellite images from $t_0$ and $t_0 + 3\text{h}$ exhibit extreme spatial correlation.
* If $t_0$ is in the training set and $t_0 + 3\text{h}$ is in the test set, models memorize the cloud pattern instead of learning generalizable meteorological physics.

### 4.2 Mathematical Partitioning Guarantee
Given the set of storms $\mathcal{S} = \{s_1, s_2, \dots, s_M\}$:
1. Storms are partitioned into mutually disjoint subsets:
   $$\mathcal{S}_{\text{train}} \cap \mathcal{S}_{\text{val}} = \emptyset, \quad \mathcal{S}_{\text{train}} \cap \mathcal{S}_{\text{test}} = \emptyset, \quad \mathcal{S}_{\text{val}} \cap \mathcal{S}_{\text{test}} = \emptyset$$
2. An assertion in the code mathematically validates that the intersection of storm IDs across all three sets is strictly empty:
   ```python
   assert len(train_storms & val_storms) == 0
   assert len(train_storms & test_storms) == 0
   assert len(val_storms & test_storms) == 0
   ```
3. Partitioning supports both:
   * **Stratified Random Splitting:** Groups storms randomly according to user-defined ratios (e.g., 70% Train, 15% Validation, 15% Test) with a fixed seed (`seed=42`).
   * **Chronological Out-of-Time Splitting:** Trains on historical storms up to year $Y$ (e.g., 1980–2020) and validates/tests on subsequent seasons (e.g., 2021–2023) to emulate operational forecast conditions.
