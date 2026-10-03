# Sprint 9 — Satellite Spatial Feature Registry & Scientific Dictionary

**Document Version:** 1.0.0  
**Date:** 2026-09-27  
**Module:** [`ml/features/satellite_spatial.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/features/satellite_spatial.py)  
**Target Horizon:** 24-Hour Tropical Cyclone Rapid Intensification ($\Delta V_{24\text{h}} \ge 30\,\text{kts}$)  
**Sensor Archive:** NOAA HURSAT-B1 v06 ($0.08^\circ \approx 8.9\,\text{km}$, $64 \times 64$ cyclone-centered grids)

---

## 1. Overview & Scientific Guiding Principles

The CycloneGuard Sprint 9 spatial baseline extracts **38 interpretable features** from multi-channel geostationary satellite imagery. Rather than treating satellite patches as uninterpretable black-box tensors, every derived metric directly models an established meteorological or structural mechanism associated with tropical cyclone intensity and eyewall organization.

### Scientific Principles:
1. **Physical Interpretability:** Every feature represents a quantifiable thermodynamic, structural, or convective property. No generic computer vision embeddings.
2. **Structural Proxies:** Features derived from radial zones (core, ring, outer) are explicitly documented as **"satellite-derived structural proxies"**, acknowledging that satellite cloud-top brightness temperatures do not directly measure surface wind speed.
3. **Strict Missing Channel Protocol:** When a channel is unavailable (e.g., nighttime visible passes), it is signaled by an explicit boolean indicator (`has_vschn = 0.0`). Missing values are **NEVER filled with zero**.
4. **NaN Handling:** Patches near domain boundaries contain valid edge-padding. All aggregations utilize NaN-ignoring statistics (`nanmean`, `nanmin`, `nanstd`).

---

## 2. Spatial Geometry & Radial Definitions

All patches are $64 \times 64$ pixels centered on the synoptic cyclone center $(y_c, x_c) = (31.5, 31.5)$. At $8.9\,\text{km}$ per pixel, the field-of-view covers approximately $570 \times 570\,\text{km}$.

| Radial Zone | Radial Distance ($r$) | Pixel Radius ($r_{\text{pix}}$) | Meteorological Target |
| :--- | :---: | :---: | :--- |
| **Inner Core** | $0 \le r \le 50\,\text{km}$ | $0 \le r_{\text{pix}} \le 5.62$ | Central Dense Overcast (CDO), eye warming, and innermost convective ring |
| **Surrounding Ring** | $50 < r \le 150\,\text{km}$ | $5.62 < r_{\text{pix}} \le 16.85$ | Primary eyewall convective ring and inner spiral rainbands |
| **Outer Region** | $150 < r \le 250\,\text{km}$ | $16.85 < r_{\text{pix}} \le 28.09$ | Outer rainbands and synoptic environmental interface |

---

## 3. Comprehensive Feature Dictionary

### Family A: IR Brightness Temperature Statistics (`IRWIN` — 10.8 µm Clean Window)

| Feature Name | Definition / Formula | Source Channel | Physical Units | Valid Range | Missing Data Behavior | Scientific Rationale |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| `irwin_mean` | Spatial mean: $\frac{1}{N}\sum T_b$ | IRWIN | Kelvin (K) | $[180.0, 320.0]$ | NaN if all NaN | Measures average cloud-top height across the cyclone domain. |
| `irwin_std` | Spatial standard deviation: $\sigma(T_b)$ | IRWIN | Kelvin (K) | $[0.0, 60.0]$ | NaN if all NaN | Reflects convective heterogeneity between cold clouds and warm ocean background. |
| `irwin_min` | Minimum brightness temperature: $\min(T_b)$ | IRWIN | Kelvin (K) | $[160.0, 260.0]$ | NaN if all NaN | Identifies the deepest, most vigorous convective cloud tops reaching the upper troposphere. |
| `irwin_p10` | 10th percentile of $T_b$ | IRWIN | Kelvin (K) | $[170.0, 280.0]$ | NaN if all NaN | Robust proxy for the coldest 10% of convective cloud tops, filtering single-pixel sensor noise. |
| `irwin_p25` | 25th percentile of $T_b$ | IRWIN | Kelvin (K) | $[180.0, 290.0]$ | NaN if all NaN | Measures the bulk convective canopy temperature. |
| `irwin_p50` | Median brightness temperature | IRWIN | Kelvin (K) | $[190.0, 305.0]$ | NaN if all NaN | Central tendency resistant to boundary outliers and clear-sky patches. |
| `irwin_p75` | 75th percentile of $T_b$ | IRWIN | Kelvin (K) | $[210.0, 315.0]$ | NaN if all NaN | Characterizes the warmer, non-convective background ocean/cirrus edge. |
| `irwin_max` | Maximum brightness temperature: $\max(T_b)$ | IRWIN | Kelvin (K) | $[260.0, 325.0]$ | NaN if all NaN | Measures warm ocean surface skin temperature in cloud-free moats or clear eyes. |
| `irwin_temp_range` | Temperature spread: $T_{\text{max}} - T_{\text{min}}$ | IRWIN | Kelvin (K) | $[10.0, 150.0]$ | NaN if all NaN | Contrast between the coldest eyewall tops and the warmest surface or eye temperatures. |
| `irwin_cold_cloud_fraction_233k` | Fraction of pixels with $T_b \le 233.15\,\text{K}$ ($-40^\circ\text{C}$) | IRWIN | Unitless $[0, 1]$ | $[0.0, 1.0]$ | NaN if all NaN | Areal extent of active deep convection in the synoptic vortex (Kaplan et al. 2010). |
| `irwin_very_cold_cloud_fraction_219k` | Fraction of pixels with $T_b \le 219.15\,\text{K}$ ($-54^\circ\text{C}$) | IRWIN | Unitless $[0, 1]$ | $[0.0, 1.0]$ | NaN if all NaN | Coverage of vigorous, sustained convective towers (Dvorak 1984, Velden et al. 2006). |
| `irwin_overshooting_fraction_203k` | Fraction of pixels with $T_b \le 203.15\,\text{K}$ ($-70^\circ\text{C}$) | IRWIN | Unitless $[0, 1]$ | $[0.0, 1.0]$ | NaN if all NaN | Convective overshooting tops penetrating the tropopause; key precursor to rapid intensification. |

---

### Family B: Core / Ring Structural Proxies (`IRWIN` — 10.8 µm Clean Window)

| Feature Name | Definition / Formula | Source Channel | Physical Units | Valid Range | Missing Data Behavior | Scientific Rationale |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| `irwin_core_mean` | Mean $T_b$ within inner core ($r \le 50\,\text{km}$) | IRWIN | Kelvin (K) | $[180.0, 310.0]$ | NaN if zone empty | Central dense overcast (CDO) temperature; colder values indicate intense core convection. |
| `irwin_core_min` | Minimum $T_b$ within inner core | IRWIN | Kelvin (K) | $[160.0, 260.0]$ | NaN if zone empty | Peak convective intensity in the central vortex. |
| `irwin_core_cold_frac` | Fraction of core pixels with $T_b \le 233.15\,\text{K}$ | IRWIN | Unitless $[0, 1]$ | $[0.0, 1.0]$ | NaN if zone empty | Degree of convective coverage directly over the storm center. |
| `irwin_core_very_cold_frac` | Fraction of core pixels with $T_b \le 219.15\,\text{K}$ | IRWIN | Unitless $[0, 1]$ | $[0.0, 1.0]$ | NaN if zone empty | Vigorous convective burst coverage in the inner core. |
| `irwin_ring_mean` | Mean $T_b$ in eyewall ring ($50 < r \le 150\,\text{km}$) | IRWIN | Kelvin (K) | $[190.0, 310.0]$ | NaN if zone empty | Mean temperature of the primary eyewall ring and surrounding inner rainbands. |
| `irwin_ring_min` | Minimum $T_b$ in eyewall ring | IRWIN | Kelvin (K) | $[170.0, 270.0]$ | NaN if zone empty | Coldest cloud top in the surrounding eyewall structure. |
| `irwin_ring_cold_frac` | Fraction of ring pixels with $T_b \le 233.15\,\text{K}$ | IRWIN | Unitless $[0, 1]$ | $[0.0, 1.0]$ | NaN if zone empty | Eyewall ring completeness / azimuthal coverage of convection. |
| `irwin_outer_mean` | Mean $T_b$ in outer region ($150 < r \le 250\,\text{km}$) | IRWIN | Kelvin (K) | $[200.0, 315.0]$ | NaN if zone empty | Surrounding synoptic environment temperature. |
| `irwin_core_ring_diff` | Radial difference: $\overline{T}_{\text{ring}} - \overline{T}_{\text{core}}$ | IRWIN | Kelvin (K) | $[-50.0, 50.0]$ | NaN if either empty | Radial temperature gradient proxy. Positive when core is colder than ring; negative when an eye clears. |
| `irwin_core_outer_diff` | Environmental contrast: $\overline{T}_{\text{outer}} - \overline{T}_{\text{core}}$ | IRWIN | Kelvin (K) | $[-30.0, 70.0]$ | NaN if either empty | Thermal contrast between the central cyclone and the ambient environment. |
| `irwin_azimuthal_std_core` | Standard deviation across 4 core quadrants | IRWIN | Kelvin (K) | $[0.0, 40.0]$ | NaN if $<2$ valid | Proxy for convective asymmetry in the inner core (high value = asymmetric/sheared; low = axisymmetric). |

---

### Family C: Spatial Texture & Gradient Descriptors (`IRWIN` — 10.8 µm Clean Window)

| Feature Name | Definition / Formula | Source Channel | Physical Units | Valid Range | Missing Data Behavior | Scientific Rationale |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| `irwin_grad_mean` | Mean spatial gradient magnitude: $\overline{\|\nabla T_b\|}$ | IRWIN | $\text{K} / \text{km}$ | $[0.0, 5.0]$ | NaN if all NaN | Overall spatial cloud-top roughness and structural boundary sharpness. |
| `irwin_grad_max` | Maximum spatial gradient magnitude: $\max(\|\nabla T_b\|)$ | IRWIN | $\text{K} / \text{km}$ | $[0.1, 15.0]$ | NaN if all NaN | Sharpest cloud-top boundary (often corresponds to the inner edge of the eyewall). |
| `irwin_local_variance` | Variance of discrete 2D Laplacian: $\operatorname{Var}(\nabla^2 T_b)$ | IRWIN | $\text{K}^2$ | $[0.0, 2000.0]$ | NaN if all NaN | Quantifies fine-scale spatial texture and cloud-top bubbling from active updrafts. |
| `irwin_spatial_entropy` | Spatial Shannon entropy of 15-bin $T_b$ histogram | IRWIN | Bits | $[0.0, 4.0]$ | NaN if all NaN | Information entropy of temperature distribution (organized storms exhibit lower entropy). |

---

### Family D: Multispectral & Water-Vapor Features (`IRWIN` vs. `IRWVP`)

| Feature Name | Definition / Formula | Source Channel | Physical Units | Valid Range | Missing Data Behavior | Scientific Rationale |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| `has_irwvp` | Availability indicator ($1.0$ if present, $0.0$ if missing) | Metadata | Binary $\{0, 1\}$ | $\{0, 1\}$ | $0.0$ | Ensures missingness is explicit; never conflated with zero temperature. |
| `irwvp_mean` | Mean upper-tropospheric water vapor $T_b$ | IRWVP (6.7 µm) | Kelvin (K) | $[200.0, 270.0]$ | NaN if missing | Broad-scale upper-tropospheric moisture content around the cyclone. |
| `irwvp_min` | Minimum water vapor brightness temperature | IRWVP (6.7 µm) | Kelvin (K) | $[180.0, 240.0]$ | NaN if missing | Coldest cloud-top water vapor emission. |
| `irwvp_core_mean` | Inner core mean water vapor $T_b$ ($r \le 50\,\text{km}$) | IRWVP (6.7 µm) | Kelvin (K) | $[190.0, 260.0]$ | NaN if missing | Moisture saturation and convective injection in the cyclone core. |
| `ir_wv_diff_mean` | Spatial mean difference: $\overline{T_{\text{IRWIN}} - T_{\text{IRWVP}}}$ | IRWIN, IRWVP | Kelvin (K) | $[-10.0, 50.0]$ | NaN if missing | Classical multispectral convective indicator (Ackerman 1996). Strong updrafts drive $T_{\text{IR}} - T_{\text{WV}} < 0$. |
| `ir_wv_core_diff` | Core difference: $\overline{T}_{\text{core, IR}} - \overline{T}_{\text{core, WV}}$ | IRWIN, IRWVP | Kelvin (K) | $[-15.0, 40.0]$ | NaN if missing | Core convective tropopause overshooting proxy. |
| `ir_wv_spatial_corr` | Pearson correlation between IRWIN and IRWVP | IRWIN, IRWVP | Unitless $[-1, 1]$ | $[-1.0, 1.0]$ | NaN if missing | Spatial coupling between upper-level moisture and cloud-top topography. |

---

### Family E: Visible Channel Structural Proxies (`VSCHN` — 0.6 µm Albedo)

| Feature Name | Definition / Formula | Source Channel | Physical Units | Valid Range | Missing Data Behavior | Scientific Rationale |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| `has_vschn` | Availability indicator ($1.0$ if daytime, $0.0$ if night) | Metadata | Binary $\{0, 1\}$ | $\{0, 1\}$ | $0.0$ | Explicit illumination flag; prevents night passes from being treated as black clouds. |
| `vschn_mean` | Mean top-of-atmosphere visible albedo reflectance | VSCHN (0.6 µm) | Fraction $[0, 1]$ | $[0.0, 1.0]$ | NaN if night | Optical thickness of cloud shield (higher albedo indicates thicker convective clouds). |
| `vschn_core_mean` | Inner core mean visible albedo ($r \le 50\,\text{km}$) | VSCHN (0.6 µm) | Fraction $[0, 1]$ | $[0.0, 1.0]$ | NaN if night | Core cloud optical depth and shadow contrast. |
| `vschn_std` | Spatial standard deviation of visible albedo | VSCHN (0.6 µm) | Fraction $[0, 1]$ | $[0.0, 0.5]$ | NaN if night | Texture roughness and shadowing from towering convective clouds. |

---

## 4. Summary of Feature Counts by Family

| Feature Family | Primary Sensor Band | Number of Features | Coverage in Dataset |
| :--- | :--- | :---: | :---: |
| **Family A (Bulk IR Statistics)** | `IRWIN` (10.8 µm Clean Window) | **12** | 347 / 347 (100.0%) |
| **Family B (Core/Ring Structural Proxies)** | `IRWIN` (Radial Concentric Masks) | **11** | 347 / 347 (100.0%) |
| **Family C (Spatial Texture & Gradients)** | `IRWIN` (2D Sobel / Laplacian / Entropy) | **4** | 347 / 347 (100.0%) |
| **Family D (Multispectral IR/WV)** | `IRWIN` + `IRWVP` (6.7 µm Water Vapor) | **7** | 347 / 347 (100.0%) |
| **Family E (Visible Channel Albedo)** | `VSCHN` (0.6 µm Visible Day-Only) | **4** | 326 / 347 (93.95%) |
| **Total Features Registered** | — | **38** | — |
