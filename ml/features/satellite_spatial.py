"""
CycloneGuard Satellite Spatial Feature Extraction Engine.
Sprint 9 - Phase 2 Deliverable.

Extracts physically and geometrically interpretable spatial features from
cyclone-centered HURSAT-B1 satellite patches (IRWIN, IRWVP, VSCHN).

Rules:
1. All features have explicit physical or meteorological interpretations.
2. Configurable physical thresholds (no unexplained magic numbers).
3. Radial zones are documented as structural proxies, not direct eyewall measurements.
4. Missing channels are signaled by explicit boolean flags; NEVER zero-filled.
5. All calculations handle NaN padding robustly.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import numpy as np


@dataclass
class SpatialFeatureConfig:
    """Configurable physical thresholds and spatial geometry parameters."""
    pixel_resolution_km: float = 8.9  # approx 0.08 deg at tropical latitudes
    patch_size_pixels: int = 64

    # Cold cloud temperature thresholds (Kelvin)
    # 233.15 K (-40°C): Standard tropical convective threshold (Kaplan et al. 2010)
    cold_cloud_threshold_k: float = 233.15
    # 219.15 K (-54°C): Very cold deep convective towers (Velden et al. 2006, Dvorak 1984)
    very_cold_cloud_threshold_k: float = 219.15
    # 203.15 K (-70°C): Vigorous convective overshooting tops near the tropopause
    overshooting_threshold_k: float = 203.15

    # Radial zone boundaries (km from cyclone center)
    core_radius_km: float = 50.0       # Inner core / central dense overcast (0 - 50 km)
    ring_radius_km: float = 150.0      # Surrounding eyewall / inner band ring (50 - 150 km)
    outer_radius_km: float = 250.0     # Outer rainband / environmental zone (150 - 250 km)


class SatelliteSpatialFeatureExtractor:
    """Extracts interpretable morphological and radiometric features from satellite patches."""

    def __init__(self, config: Optional[SpatialFeatureConfig] = None):
        self.config = config or SpatialFeatureConfig()
        self._init_radial_masks()

    def _init_radial_masks(self):
        """Precomputes concentric radial distance grids in kilometers."""
        size = self.config.patch_size_pixels
        center = (size - 1) / 2.0  # Center is (31.5, 31.5) for 64x64 grid
        y, x = np.ogrid[:size, :size]
        dist_pixels = np.sqrt((y - center) ** 2 + (x - center) ** 2)
        dist_km = dist_pixels * self.config.pixel_resolution_km

        self.mask_core = dist_km <= self.config.core_radius_km
        self.mask_ring = (dist_km > self.config.core_radius_km) & (dist_km <= self.config.ring_radius_km)
        self.mask_outer = (dist_km > self.config.ring_radius_km) & (dist_km <= self.config.outer_radius_km)
        self.dist_km = dist_km

    # -------------------------------------------------------------------------
    # A. IRWIN Statistical Features (Clean Window 10.8 µm)
    # -------------------------------------------------------------------------
    def extract_irwin_statistics(self, irwin_patch: np.ndarray) -> Dict[str, float]:
        """
        Extracts bulk temperature distribution statistics from clean IR window (10.8 µm).
        Reflects overall convective cloud-top altitudes and clear-sky background.
        """
        valid = irwin_patch[~np.isnan(irwin_patch)]
        if valid.size == 0:
            return {
                "irwin_mean": np.nan,
                "irwin_std": np.nan,
                "irwin_min": np.nan,
                "irwin_p10": np.nan,
                "irwin_p25": np.nan,
                "irwin_p50": np.nan,
                "irwin_p75": np.nan,
                "irwin_max": np.nan,
                "irwin_temp_range": np.nan,
                "irwin_cold_cloud_fraction_233k": np.nan,
                "irwin_very_cold_cloud_fraction_219k": np.nan,
                "irwin_overshooting_fraction_203k": np.nan,
            }

        p10, p25, p50, p75 = np.percentile(valid, [10, 25, 50, 75])
        min_v = float(np.min(valid))
        max_v = float(np.max(valid))

        return {
            "irwin_mean": float(np.mean(valid)),
            "irwin_std": float(np.std(valid)),
            "irwin_min": min_v,
            "irwin_p10": float(p10),
            "irwin_p25": float(p25),
            "irwin_p50": float(p50),
            "irwin_p75": float(p75),
            "irwin_max": max_v,
            "irwin_temp_range": float(max_v - min_v),
            "irwin_cold_cloud_fraction_233k": float(np.mean(valid <= self.config.cold_cloud_threshold_k)),
            "irwin_very_cold_cloud_fraction_219k": float(np.mean(valid <= self.config.very_cold_cloud_threshold_k)),
            "irwin_overshooting_fraction_203k": float(np.mean(valid <= self.config.overshooting_threshold_k)),
        }

    # -------------------------------------------------------------------------
    # B. Core / Ring Structural Proxies (IRWIN)
    # -------------------------------------------------------------------------
    def extract_core_ring_features(self, irwin_patch: np.ndarray) -> Dict[str, float]:
        """
        Extracts radial zone temperature statistics relative to cyclone center.
        Provides structural proxies for central dense overcast (CDO), eye warming,
        and eyewall convective symmetry.
        """
        core_vals = irwin_patch[self.mask_core & ~np.isnan(irwin_patch)]
        ring_vals = irwin_patch[self.mask_ring & ~np.isnan(irwin_patch)]
        outer_vals = irwin_patch[self.mask_outer & ~np.isnan(irwin_patch)]

        core_mean = float(np.mean(core_vals)) if core_vals.size > 0 else np.nan
        core_min = float(np.min(core_vals)) if core_vals.size > 0 else np.nan
        core_cold_frac = float(np.mean(core_vals <= self.config.cold_cloud_threshold_k)) if core_vals.size > 0 else np.nan
        core_very_cold_frac = float(np.mean(core_vals <= self.config.very_cold_cloud_threshold_k)) if core_vals.size > 0 else np.nan

        ring_mean = float(np.mean(ring_vals)) if ring_vals.size > 0 else np.nan
        ring_min = float(np.min(ring_vals)) if ring_vals.size > 0 else np.nan
        ring_cold_frac = float(np.mean(ring_vals <= self.config.cold_cloud_threshold_k)) if ring_vals.size > 0 else np.nan

        outer_mean = float(np.mean(outer_vals)) if outer_vals.size > 0 else np.nan

        # Radial temperature differences:
        # ring_mean - core_mean: positive if core is colder/deeper than surrounding ring
        diff_ring_core = (ring_mean - core_mean) if (np.isfinite(ring_mean) and np.isfinite(core_mean)) else np.nan
        diff_outer_core = (outer_mean - core_mean) if (np.isfinite(outer_mean) and np.isfinite(core_mean)) else np.nan

        # Azimuthal asymmetry proxy in the inner core
        # (Standard deviation across 4 quadrant sectors in core)
        azimuthal_std = self._compute_quadrant_asymmetry(irwin_patch, self.mask_core)

        return {
            "irwin_core_mean": core_mean,
            "irwin_core_min": core_min,
            "irwin_core_cold_frac": core_cold_frac,
            "irwin_core_very_cold_frac": core_very_cold_frac,
            "irwin_ring_mean": ring_mean,
            "irwin_ring_min": ring_min,
            "irwin_ring_cold_frac": ring_cold_frac,
            "irwin_outer_mean": outer_mean,
            "irwin_core_ring_diff": diff_ring_core,
            "irwin_core_outer_diff": diff_outer_core,
            "irwin_azimuthal_std_core": azimuthal_std,
        }

    def _compute_quadrant_asymmetry(self, patch: np.ndarray, base_mask: np.ndarray) -> float:
        """Computes standard deviation of mean brightness temperature across 4 quadrants."""
        size = self.config.patch_size_pixels
        center = (size - 1) / 2.0
        y, x = np.ogrid[:size, :size]

        q1 = (y <= center) & (x >= center) & base_mask & ~np.isnan(patch)  # NE
        q2 = (y <= center) & (x < center) & base_mask & ~np.isnan(patch)   # NW
        q3 = (y > center) & (x < center) & base_mask & ~np.isnan(patch)    # SW
        q4 = (y > center) & (x >= center) & base_mask & ~np.isnan(patch)   # SE

        q_means = []
        for q_mask in [q1, q2, q3, q4]:
            vals = patch[q_mask]
            if vals.size > 0:
                q_means.append(float(np.mean(vals)))

        if len(q_means) >= 2:
            return float(np.std(q_means))
        return np.nan

    # -------------------------------------------------------------------------
    # C. Spatial Texture & Gradient Features (IRWIN)
    # -------------------------------------------------------------------------
    def extract_spatial_texture(self, irwin_patch: np.ndarray) -> Dict[str, float]:
        """
        Extracts spatial gradient magnitude and texture roughness indicators.
        Sharp gradient boundaries correspond to well-defined eyewall edges.
        """
        # Replace NaNs with local mean for gradient filter computation
        patch_clean = irwin_patch.copy()
        nan_mask = np.isnan(patch_clean)
        if nan_mask.all():
            return {
                "irwin_grad_mean": np.nan,
                "irwin_grad_max": np.nan,
                "irwin_local_variance": np.nan,
                "irwin_spatial_entropy": np.nan,
            }

        valid_mean = float(np.nanmean(patch_clean))
        patch_clean[nan_mask] = valid_mean

        # Sobel-like discrete gradients in physical units (K / km)
        gy, gx = np.gradient(patch_clean, self.config.pixel_resolution_km)
        grad_mag = np.sqrt(gx ** 2 + gy ** 2)
        grad_mag[nan_mask] = np.nan

        valid_grads = grad_mag[~np.isnan(grad_mag)]
        grad_mean = float(np.mean(valid_grads)) if valid_grads.size > 0 else np.nan
        grad_max = float(np.max(valid_grads)) if valid_grads.size > 0 else np.nan

        # High-pass / Laplacian texture variance
        # Discrete 3x3 Laplacian kernel
        lap = (
            np.roll(patch_clean, 1, axis=0) + np.roll(patch_clean, -1, axis=0) +
            np.roll(patch_clean, 1, axis=1) + np.roll(patch_clean, -1, axis=1) -
            4.0 * patch_clean
        )[1:-1, 1:-1]
        local_var = float(np.var(lap))

        # Spatial Shannon entropy of brightness temperature distribution (10 K bins)
        valid_t = irwin_patch[~nan_mask]
        if valid_t.size > 0:
            hist, _ = np.histogram(valid_t, bins=15, range=(170.0, 320.0), density=True)
            hist = hist[hist > 0]
            entropy = float(-np.sum(hist * np.log2(hist)))
        else:
            entropy = np.nan

        return {
            "irwin_grad_mean": grad_mean,
            "irwin_grad_max": grad_max,
            "irwin_local_variance": local_var,
            "irwin_spatial_entropy": entropy,
        }

    # -------------------------------------------------------------------------
    # D. IR / Water-Vapor Relationship (IRWIN vs IRWVP)
    # -------------------------------------------------------------------------
    def extract_multispectral_relationship(
        self,
        irwin_patch: np.ndarray,
        irwvp_patch: Optional[np.ndarray],
    ) -> Dict[str, float]:
        """
        Calculates bivariate relationships between IR window and Upper Tropospheric Water Vapor.
        Negative difference (T_IRWIN - T_IRWVP < 0) signifies deep convective penetration
        into the lower stratosphere (overshooting convective updrafts).
        """
        if irwvp_patch is None or np.isnan(irwvp_patch).all():
            return {
                "has_irwvp": 0.0,
                "irwvp_mean": np.nan,
                "irwvp_min": np.nan,
                "irwvp_core_mean": np.nan,
                "ir_wv_diff_mean": np.nan,
                "ir_wv_core_diff": np.nan,
                "ir_wv_spatial_corr": np.nan,
            }

        valid_wv = irwvp_patch[~np.isnan(irwvp_patch)]
        irwvp_mean = float(np.mean(valid_wv)) if valid_wv.size > 0 else np.nan
        irwvp_min = float(np.min(valid_wv)) if valid_wv.size > 0 else np.nan

        core_wv = irwvp_patch[self.mask_core & ~np.isnan(irwvp_patch)]
        irwvp_core_mean = float(np.mean(core_wv)) if core_wv.size > 0 else np.nan

        # Co-located valid mask
        joint_mask = ~np.isnan(irwin_patch) & ~np.isnan(irwvp_patch)
        if joint_mask.sum() > 10:
            diff_patch = irwin_patch[joint_mask] - irwvp_patch[joint_mask]
            diff_mean = float(np.mean(diff_patch))

            # Core difference
            core_joint = joint_mask & self.mask_core
            if core_joint.sum() > 5:
                diff_core = float(np.mean(irwin_patch[core_joint] - irwvp_patch[core_joint]))
            else:
                diff_core = np.nan

            # Pearson correlation
            ir_flat = irwin_patch[joint_mask]
            wv_flat = irwvp_patch[joint_mask]
            if np.std(ir_flat) > 1e-4 and np.std(wv_flat) > 1e-4:
                corr = float(np.corrcoef(ir_flat, wv_flat)[0, 1])
            else:
                corr = 0.0
        else:
            diff_mean = np.nan
            diff_core = np.nan
            corr = np.nan

        return {
            "has_irwvp": 1.0,
            "irwvp_mean": irwvp_mean,
            "irwvp_min": irwvp_min,
            "irwvp_core_mean": irwvp_core_mean,
            "ir_wv_diff_mean": diff_mean,
            "ir_wv_core_diff": diff_core,
            "ir_wv_spatial_corr": corr,
        }

    # -------------------------------------------------------------------------
    # E. Visible Channel Structural Proxies (VSCHN)
    # -------------------------------------------------------------------------
    def extract_visible_features(self, vschn_patch: Optional[np.ndarray]) -> Dict[str, float]:
        """
        Extracts top-of-atmosphere visible albedo structural statistics when daytime
        illumination is available. Returns NaN and has_vschn=0.0 during night passes.
        """
        if vschn_patch is None:
            return {
                "has_vschn": 0.0,
                "vschn_mean": np.nan,
                "vschn_core_mean": np.nan,
                "vschn_std": np.nan,
            }

        # Filter out invalid negative calibration values or missing pixels
        valid_mask = ~np.isnan(vschn_patch) & (vschn_patch >= 0.0)
        valid = vschn_patch[valid_mask]

        if valid.size < 20:
            return {
                "has_vschn": 0.0,
                "vschn_mean": np.nan,
                "vschn_core_mean": np.nan,
                "vschn_std": np.nan,
            }

        core_vals = vschn_patch[self.mask_core & valid_mask]
        core_mean = float(np.mean(core_vals)) if core_vals.size > 0 else np.nan

        return {
            "has_vschn": 1.0,
            "vschn_mean": float(np.mean(valid)),
            "vschn_core_mean": core_mean,
            "vschn_std": float(np.std(valid)),
        }

    # -------------------------------------------------------------------------
    # Full Extraction Pipeline
    # -------------------------------------------------------------------------
    def extract_all_features(
        self,
        irwin_patch: np.ndarray,
        irwvp_patch: Optional[np.ndarray] = None,
        vschn_patch: Optional[np.ndarray] = None,
    ) -> Dict[str, float]:
        """
        Extracts all 38 interpretable spatial features from available channels for one fix.
        """
        feats: Dict[str, float] = {}
        feats.update(self.extract_irwin_statistics(irwin_patch))
        feats.update(self.extract_core_ring_features(irwin_patch))
        feats.update(self.extract_spatial_texture(irwin_patch))
        feats.update(self.extract_multispectral_relationship(irwin_patch, irwvp_patch))
        feats.update(self.extract_visible_features(vschn_patch))
        return feats
