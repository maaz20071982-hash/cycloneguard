# CycloneGuard Centralized Feature Registry

**Version:** 1.0.0  
**Sprint:** 5 — AI Data Fusion & Cyclone State Engine  
**Module:** [`ml/features/registry.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/features/registry.py)

---

## 1. Scientific Governance & Rules

1. **Zero Invented Features:** No feature definition is permitted unless supported by actual ingested physical measurements or mathematically grounded derivations.
2. **Metadata Completeness:** Every feature must register its provider source, source physical variable, exact unit of measurement, and operational description.
3. **Physical Distinction:** Statistical properties of radiance images (e.g. brightness temperature gradients) are strictly cataloged as radiometric properties and separated from meteorological quantities (e.g. surface pressure).
4. **Registry Immutability:** Features once registered cannot have their naming or physical interpretation silently modified.

---

## 2. Complete Registered Feature Catalog

### 1. Track & Intensity Features (`FeatureCategory.TRACK`)
*Primary Source: `noaa_ibtracs`*

| Feature Name | Type | Physical Variable | Unit | Description |
|---|---|---|---|---|
| `track_latitude` | Numerical | `lat` | degrees_north | Latitude of storm center (-90 to +90) |
| `track_longitude` | Numerical | `lon` | degrees_east | Longitude of storm center (-180 to +180) |
| `track_wind_speed` | Numerical | `usa_wind` | knots | Maximum 1-minute sustained wind speed |
| `track_pressure` | Numerical | `usa_pres` | mb | Minimum central atmospheric pressure |
| `track_translation_speed_kts` | Numerical | Derived Kinematic | knots | Great-circle forward motion speed over 6h |
| `track_translation_bearing_deg` | Numerical | Derived Kinematic | degrees | Forward direction bearing (0 to 360 degrees) |

---

### 2. Satellite Radiometric Features (`FeatureCategory.SATELLITE`)
*Primary Source: `noaa_hursat_b1` (Band B1 Infrared, 10.8 µm)*

| Feature Name | Type | Physical Variable | Unit | Description |
|---|---|---|---|---|
| `sat_ir_min_temp` | Numerical | `ch1_ir_kelvin` | Kelvin | Minimum brightness temperature across storm crop |
| `sat_ir_mean_temp` | Numerical | `ch1_ir_kelvin` | Kelvin | Mean brightness temperature across valid pixels |
| `sat_ir_std_temp` | Numerical | `ch1_ir_kelvin` | Kelvin | Standard deviation of brightness temperature |
| `sat_ir_p10_temp` | Numerical | `ch1_ir_kelvin` | Kelvin | 10th percentile brightness temperature |
| `sat_ir_p50_temp` | Numerical | `ch1_ir_kelvin` | Kelvin | Median brightness temperature across crop |
| `sat_ir_core_temp` | Numerical | `ch1_ir_kelvin` | Kelvin | Mean brightness temperature in inner core ($r \le 50\,\text{km}$) |
| `sat_ir_ring_temp` | Numerical | `ch1_ir_kelvin` | Kelvin | Mean brightness temperature in eyewall ring ($50 < r \le 150\,\text{km}$) |
| `sat_ir_eye_surround_diff` | Numerical | `ch1_ir_kelvin` | Kelvin | Core-to-ring contrast ($T_{\text{core}} - T_{\text{ring}}$) |
| `sat_cold_cloud_fraction_200k` | Numerical | Convective Coverage | fraction | Fraction of valid pixels with $T < 200\,\text{K}$ |
| `sat_cold_cloud_fraction_210k` | Numerical | Convective Coverage | fraction | Fraction of valid pixels with $T < 210\,\text{K}$ |
| `sat_cold_cloud_fraction_220k` | Numerical | Convective Coverage | fraction | Fraction of valid pixels with $T < 220\,\text{K}$ |

---

### 3. Spatial Morphology Features (`FeatureCategory.MORPHOLOGY`)
*Primary Source: `noaa_hursat_b1`*

| Feature Name | Type | Physical Variable | Unit | Description |
|---|---|---|---|---|
| `morph_radial_symmetry` | Numerical | Spatial Geometry | score (0-1) | Azimuthal symmetry score across 4 concentric rings |
| `morph_convective_organization` | Numerical | Spatial Pattern | score (0-1) | Ratio of cold cloud coverage in inner 100km to outer 300km |
| `morph_eye_detected` | Boolean | Algorithmic Structure | boolean | True only if inner core is $\ge 3\,\text{K}$ warmer than cold ring |
| `morph_eye_temperature_contrast` | Numerical | Thermal Gradient | Kelvin | Quantitative temperature difference between eye and surrounding ring |

---

### 4. Temporal Dynamic Features (`FeatureCategory.TEMPORAL`)
*Primary Sources: Historical track sequence & satellite series*

| Feature Name | Type | Physical Variable | Unit | Description |
|---|---|---|---|---|
| `temp_delta_wind_6h` | Numerical | $\Delta V_{6h}$ | knots | 6-hour change in maximum sustained wind speed |
| `temp_delta_wind_12h` | Numerical | $\Delta V_{12h}$ | knots | 12-hour change in maximum sustained wind speed |
| `temp_delta_pressure_6h` | Numerical | $\Delta P_{6h}$ | mb | 6-hour change in central atmospheric pressure |
| `temp_wind_change_rate_per_hour` | Numerical | $dV/dt$ | kts/hr | Instantaneous hourly rate of wind speed change |
| `temp_delta_ir_min_6h` | Numerical | $\Delta T_{\min,6h}$ | Kelvin | 6-hour change in minimum cloud-top brightness temperature |

---

### 5. Cross-Source Physical Consistency (`FeatureCategory.CROSS_SOURCE`)
*Primary Sources: Multi-sensor comparison*

| Feature Name | Type | Physical Variable | Unit | Description |
|---|---|---|---|---|
| `cross_intensity_agreement` | Categorical | Multi-sensor agreement | code | `consistent`, `partially_consistent`, `disagreeing`, or `insufficient_evidence` |
| `cross_adt_track_diff_kts` | Numerical | Objective vs ground truth | knots | Difference between ADT objective wind and IBTrACS best-track |
| `cross_convection_wind_plausibility` | Numerical | Physical consistency | score (0-1) | Concordance between deep convective area and surface wind speed |

---

### 6. Data Quality & Observational Coverage (`FeatureCategory.DATA_QUALITY`)
*Primary Sources: Ingestion telemetry & alignment metadata*

| Feature Name | Type | Physical Variable | Unit | Description |
|---|---|---|---|---|
| `quality_track_available` | Boolean | Sensor Status | boolean | IBTrACS best-track observation is available at timestamp |
| `quality_ir_available` | Boolean | Sensor Status | boolean | HURSAT-B1 infrared imagery is available at timestamp |
| `quality_adt_available` | Boolean | Sensor Status | boolean | Advanced Dvorak Technique objective fix available |
| `quality_insat_available` | Boolean | Sensor Status | boolean | INSAT-3D/3DR geostationary imagery available |
| `quality_scatterometer_available` | Boolean | Sensor Status | boolean | MetOp ASCAT ocean surface wind vector pass available |
| `quality_microwave_available` | Boolean | Sensor Status | boolean | GPM GMI passive microwave overpass available |
| `quality_temporal_gap_minutes` | Numerical | Alignment Offset | minutes | Temporal offset between track fix and satellite scan |
| `quality_is_boundary_padded` | Boolean | Alignment Quality | boolean | True if storm crop required edge padding (near swath edge) |
| `quality_missing_pixels_fraction` | Numerical | Alignment Quality | fraction | Ratio of missing/corrupt pixels inside the 101x101 crop |
| `quality_overall_flag` | Categorical | Telemetry Tier | flag | `GOOD`, `ACCEPTABLE`, `PARTIAL_TRACK_ONLY`, `DEGRADED`, or `INVALID` |

---

## 3. Querying the Feature Registry

```python
from ml.features.registry import FeatureRegistry, FeatureCategory

reg = FeatureRegistry()

# 1. Total feature count
print(f"Total registered features: {len(reg.list_all())}")

# 2. Inspect a specific feature definition
feat = reg.get("morph_eye_detected")
print(f"Name: {feat.name}, Unit: {feat.unit}, Source: {feat.source}")

# 3. Retrieve all features in a category
temporal_features = reg.get_by_category(FeatureCategory.TEMPORAL)
for f in temporal_features:
    print(f" - {f.name} ({f.unit})")
```
