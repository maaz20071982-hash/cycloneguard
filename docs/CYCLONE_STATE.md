# CycloneGuard Cyclone State Representation Specification

**Version:** 1.0.0 (`state_schema_v1`)  
**Sprint:** 5 — AI Data Fusion & Cyclone State Engine  
**Status:** Approved & Frozen

---

## 1. Overview & Objective

The **Cyclone State** is the unified, scientifically inspectable representation of a tropical cyclone at a discrete timestamp $t_0$. Rather than passing raw satellite imagery, sparse track tables, and sensor files directly into black-box neural networks, CycloneGuard transforms heterogeneous observational streams into a standardized, provenance-tracked `CycloneState` schema.

Every feature within the cyclone state preserves:
1. **Source identity** (e.g. `noaa_ibtracs`, `noaa_hursat_b1`)
2. **Physical variable & unit** (e.g. `knots`, `mb`, `Kelvin`, `km/h`, `degrees`)
3. **Observation timestamp in UTC**
4. **Spatial alignment context** (center coordinates, crop resolution)
5. **Observational availability flag** (explicit distinction between true zero and unobserved)

---

## 2. CycloneState Object Schema

Implemented in [`ml/features/cyclone_state.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/features/cyclone_state.py), the `CycloneState` object contains the following core structural blocks:

```json
{
  "storm_id": "2023129N08091",
  "storm_name": "MOCHA",
  "timestamp_utc": "2023-05-11T12:00:00Z",
  "schema_version": "state_schema_v1",
  "location": {
    "latitude": 12.5,
    "longitude": 87.8
  },
  "intensity": {
    "value": 65.0,
    "unit": "knots",
    "source": "noaa_ibtracs",
    "central_pressure_mb": 982.0
  },
  "track_features": {
    "track_latitude": 12.5,
    "track_longitude": 87.8,
    "track_wind_speed": 65.0,
    "track_pressure": 982.0,
    "track_translation_speed_kts": 6.8,
    "track_translation_bearing_deg": 348.5
  },
  "satellite_features": {
    "sat_ir_min_temp": 194.5,
    "sat_ir_mean_temp": 248.2,
    "sat_ir_std_temp": 22.4,
    "sat_ir_p10_temp": 210.1,
    "sat_ir_p50_temp": 252.3,
    "sat_ir_core_temp": 235.8,
    "sat_ir_ring_temp": 212.1,
    "sat_ir_eye_surround_diff": 23.7,
    "sat_cold_cloud_fraction_200k": 0.082,
    "sat_cold_cloud_fraction_210k": 0.164,
    "sat_cold_cloud_fraction_220k": 0.285
  },
  "morphology_features": {
    "morph_radial_symmetry": 0.84,
    "morph_convective_organization": 0.76,
    "morph_eye_detected": true,
    "morph_eye_temperature_contrast": 23.7
  },
  "temporal_features": {
    "temp_delta_wind_6h": 15.0,
    "temp_delta_wind_12h": 25.0,
    "temp_delta_pressure_6h": -10.0,
    "temp_wind_change_rate_per_hour": 2.5,
    "temp_delta_ir_min_6h": -8.5
  },
  "cross_source_features": {
    "cross_intensity_agreement": "insufficient_evidence",
    "cross_adt_track_diff_kts": null,
    "cross_convection_wind_plausibility": 1.0
  },
  "data_quality": {
    "quality_track_available": true,
    "quality_ir_available": true,
    "quality_adt_available": false,
    "quality_insat_available": false,
    "quality_scatterometer_available": false,
    "quality_microwave_available": false,
    "quality_temporal_gap_minutes": 14.2,
    "quality_is_boundary_padded": false,
    "quality_missing_pixels_fraction": 0.0012,
    "quality_overall_flag": "GOOD"
  },
  "available_sources": ["noaa_ibtracs", "noaa_hursat_b1"],
  "missing_sources": ["insat_mosdac", "adt_dvorak", "ascat_metop", "gpm_gmi"]
}
```

---

## 3. Cyclone State Numerical Vector Encoder (`state_schema_v1`)

To interface with downstream predictive machine learning algorithms without data ambiguity, the `CycloneStateEncoder` in [`ml/features/state_encoder.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/features/state_encoder.py) flattens the structured representation into a fixed-length numerical vector $\mathbf{x} \in \mathbb{R}^{69}$.

### Dual-Channel Representation: Distinguishing Zero from Unobserved
For every continuous physical feature $k$ (e.g. `track_wind_speed`, `sat_ir_min_temp`), the encoder generates **two adjacent vector elements**:
1. $x_{k,\text{val}}$: The physical measurement if observed, or the training-split median fallback if unobserved.
2. $x_{k,\text{is\_observed}} \in \{0.0, 1.0\}$: Binary indicator flag indicating whether $x_{k}$ represents an actual observation ($1.0$) or an absent/missing observation ($0.0$).

This architectural pattern guarantees that:
- A measured wind speed of 0.0 kts (quiescent disturbance) has $x_{\text{val}} = 0.0$ and $x_{\text{is\_observed}} = 1.0$.
- A missing satellite observation where wind speed is unmeasured has $x_{\text{val}} = 0.0$ and $x_{\text{is\_observed}} = 0.0$.
- Future linear, tree-based, and deep learning architectures can cleanly identify observational missingness.

### Vector Dimension Allocation ($D=69$)
| Category | Base Features | Generated Channels | Sub-Dimension |
|---|---|---|---|
| Track Kinematics | 6 | Value + Observed Flag | 12 |
| Satellite Radiometry | 11 | Value + Observed Flag | 22 |
| Spatial Morphology | 4 | Value + Observed Flag | 8 |
| Temporal Dynamics | 5 | Value + Observed Flag | 10 |
| Cross-Source Plausibility | 2 | Value + Observed Flag | 4 |
| Quality Numeric (Gap, Pixels) | 2 | Value + Observed Flag | 4 |
| Categorical Encodings | 2 | Integer Code | 2 |
| Sensor Availability Flags | 7 | Binary 0/1 Flag | 7 |
| **Total Vector Dimension** | **32** | — | **69** |

---

## 4. Usage Example

```python
from ml.data.schemas.track import CycloneTrackPoint
from ml.features.cyclone_state import CycloneStateBuilder
from ml.features.state_encoder import CycloneStateEncoder

# 1. Build observation track point
track_pt = CycloneTrackPoint(
    storm_id="2023129N08091",
    storm_name="MOCHA",
    season=2023,
    basin="NI",
    timestamp_utc="2023-05-11T12:00:00Z",
    latitude=12.5,
    longitude=87.8,
    wind_speed_kts=65.0,
    central_pressure_mb=982.0,
)

# 2. Build structured CycloneState (with optional satellite crop and history)
state = CycloneStateBuilder.build_state(
    current_track=track_pt,
    sat_crop=mocha_satellite_crop,
    prev_track=previous_6h_track_pt,
)

# 3. Encode into 69-dimensional vector
encoder = CycloneStateEncoder()
vector = encoder.encode(state)
assert vector.shape == (69,)
```
