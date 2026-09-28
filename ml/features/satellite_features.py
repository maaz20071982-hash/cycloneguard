"""
CycloneGuard Satellite & Morphology Feature Extraction.

Extracts inspectable physical and spatial morphology features from 2D infrared
brightness temperature fields centered on the cyclone:
- Spatial statistics & percentiles
- Deep convective cold-cloud fractional coverage (<200K, <210K, <220K)
- Inner core (r <= 50 km) vs. eyewall ring (50 < r <= 150 km) thermal contrast
- Azimuthal radial symmetry score
- Convective organization index
- Algorithmic warm eye detection and contrast
"""

import math
from typing import Any, Dict, Optional, Tuple
import numpy as np


class SatelliteFeatureExtractor:
    """
    Extracts spatial, radiometric, and morphological features from storm-centered IR rasters.
    """

    @classmethod
    def extract_from_crop(
        cls,
        ir_array: np.ndarray,
        pixel_resolution_deg: float = 0.08,
        center_row_col: Optional[Tuple[int, int]] = None,
    ) -> Dict[str, Any]:
        """
        Extract complete satellite and morphology features from a 2D IR brightness temperature array (Kelvin).
        
        Args:
            ir_array: 2D numpy array of brightness temperatures in Kelvin.
            pixel_resolution_deg: Grid resolution in degrees (default ~0.08 deg ≈ 8.88 km).
            center_row_col: Tuple (row, col) of the cyclone center. Defaults to grid center.
        """
        if ir_array is None or ir_array.size == 0:
            return cls._empty_features()

        # Mask out NaN and fill values (<100K or >400K)
        valid_mask = np.isfinite(ir_array) & (ir_array >= 100.0) & (ir_array <= 400.0)
        valid_values = ir_array[valid_mask]

        if len(valid_values) == 0:
            return cls._empty_features()

        # Spatial basic statistics
        min_temp = float(np.min(valid_values))
        mean_temp = float(np.mean(valid_values))
        std_temp = float(np.std(valid_values))
        p10_temp = float(np.percentile(valid_values, 10))
        p50_temp = float(np.percentile(valid_values, 50))

        # Convective cold-cloud fractional coverage
        total_valid = float(len(valid_values))
        frac_200k = float(np.sum(valid_values < 200.0) / total_valid)
        frac_210k = float(np.sum(valid_values < 210.0) / total_valid)
        frac_220k = float(np.sum(valid_values < 220.0) / total_valid)

        # Coordinate grid relative to cyclone center
        h, w = ir_array.shape
        if center_row_col is None:
            cr, cc = h // 2, w // 2
        else:
            cr, cc = center_row_col

        # Grid distance from center in kilometers (1 deg ≈ 111 km)
        km_per_deg = 111.0
        km_per_pixel = pixel_resolution_deg * km_per_deg
        
        y_indices, x_indices = np.indices((h, w))
        dist_pixels = np.sqrt((y_indices - cr) ** 2 + (x_indices - cc) ** 2)
        dist_km = dist_pixels * km_per_pixel

        # Core radius (r <= 50 km) and ring radius (50 km < r <= 150 km)
        core_mask = valid_mask & (dist_km <= 50.0)
        ring_mask = valid_mask & (dist_km > 50.0) & (dist_km <= 150.0)

        core_temp = float(np.mean(ir_array[core_mask])) if np.any(core_mask) else mean_temp
        ring_temp = float(np.mean(ir_array[ring_mask])) if np.any(ring_mask) else mean_temp
        eye_surround_diff = core_temp - ring_temp

        # Convective organization index: fraction of deep convection (<210K) inside 100 km
        convective_domain = valid_mask & (ir_array < 210.0)
        total_deep_convective = np.sum(convective_domain)
        if total_deep_convective > 0:
            inner_deep_convective = np.sum(convective_domain & (dist_km <= 100.0))
            convective_org_index = float(inner_deep_convective / total_deep_convective)
        else:
            convective_org_index = 0.0

        # Azimuthal radial symmetry score
        radial_symmetry = cls._compute_radial_symmetry(ir_array, valid_mask, dist_km, cr, cc)

        # Algorithmic warm eye detection
        eye_detected, eye_contrast = cls._detect_eye_feature(
            ir_array=ir_array,
            valid_mask=valid_mask,
            dist_km=dist_km,
            core_temp=core_temp,
            ring_temp=ring_temp,
            eye_surround_diff=eye_surround_diff,
        )

        return {
            "sat_ir_min_temp": round(min_temp, 2),
            "sat_ir_mean_temp": round(mean_temp, 2),
            "sat_ir_std_temp": round(std_temp, 2),
            "sat_ir_p10_temp": round(p10_temp, 2),
            "sat_ir_p50_temp": round(p50_temp, 2),
            "sat_ir_core_temp": round(core_temp, 2),
            "sat_ir_ring_temp": round(ring_temp, 2),
            "sat_ir_eye_surround_diff": round(eye_surround_diff, 2),
            "sat_cold_cloud_fraction_200k": round(frac_200k, 4),
            "sat_cold_cloud_fraction_210k": round(frac_210k, 4),
            "sat_cold_cloud_fraction_220k": round(frac_220k, 4),
            "morph_radial_symmetry": round(radial_symmetry, 4),
            "morph_convective_organization": round(convective_org_index, 4),
            "morph_eye_detected": eye_detected,
            "morph_eye_temperature_contrast": round(eye_contrast, 2),
        }

    @staticmethod
    def _compute_radial_symmetry(
        ir_array: np.ndarray,
        valid_mask: np.ndarray,
        dist_km: np.ndarray,
        cr: int,
        cc: int,
    ) -> float:
        """
        Compute azimuthal radial symmetry by measuring temperature variance
        across angular sectors in concentric annuli.
        """
        # Calculate polar angles
        h, w = ir_array.shape
        y_indices, x_indices = np.indices((h, w))
        angles = np.arctan2(y_indices - cr, x_indices - cc)  # -pi to +pi

        # 4 concentric radial rings: 25-50km, 50-100km, 100-150km, 150-200km
        rings = [(25.0, 50.0), (50.0, 100.0), (100.0, 150.0), (150.0, 200.0)]
        num_sectors = 8
        sector_edges = np.linspace(-np.pi, np.pi, num_sectors + 1)

        ring_variances = []
        for r_min, r_max in rings:
            ring_mask = valid_mask & (dist_km >= r_min) & (dist_km < r_max)
            if not np.any(ring_mask):
                continue

            sector_means = []
            for s in range(num_sectors):
                s_mask = ring_mask & (angles >= sector_edges[s]) & (angles < sector_edges[s + 1])
                if np.any(s_mask):
                    sector_means.append(float(np.mean(ir_array[s_mask])))

            if len(sector_means) >= 4:
                ring_variances.append(float(np.std(sector_means)))

        if not ring_variances:
            return 0.5  # Neutral fallback

        avg_azimuthal_std = float(np.mean(ring_variances))
        # Symmetry formula: lower standard deviation = higher symmetry score (0.0 to 1.0)
        symmetry_score = 1.0 / (1.0 + (avg_azimuthal_std / 10.0))
        return float(np.clip(symmetry_score, 0.0, 1.0))

    @staticmethod
    def _detect_eye_feature(
        ir_array: np.ndarray,
        valid_mask: np.ndarray,
        dist_km: np.ndarray,
        core_temp: float,
        ring_temp: float,
        eye_surround_diff: float,
    ) -> Tuple[bool, float]:
        """
        Algorithmically evaluate whether a warm eye feature is present:
        Requires:
        1. Inner core (r <= 50 km) is warmer than surrounding ring (50 < r <= 150 km) by >= 3 K.
        2. Eyewall ring contains cold convective cloud (<240 K).
        """
        if eye_surround_diff < 3.0:
            return False, 0.0

        ring_mask = valid_mask & (dist_km > 50.0) & (dist_km <= 150.0)
        if not np.any(ring_mask):
            return False, 0.0

        min_ring_temp = float(np.min(ir_array[ring_mask]))
        # A true eye must be bounded by convective cloud tops (cold ring)
        if min_ring_temp < 240.0 and eye_surround_diff >= 3.0:
            return True, float(eye_surround_diff)

        return False, 0.0

    @classmethod
    def _empty_features(cls) -> Dict[str, Any]:
        """Return null values when no satellite data is available."""
        return {
            "sat_ir_min_temp": None,
            "sat_ir_mean_temp": None,
            "sat_ir_std_temp": None,
            "sat_ir_p10_temp": None,
            "sat_ir_p50_temp": None,
            "sat_ir_core_temp": None,
            "sat_ir_ring_temp": None,
            "sat_ir_eye_surround_diff": None,
            "sat_cold_cloud_fraction_200k": None,
            "sat_cold_cloud_fraction_210k": None,
            "sat_cold_cloud_fraction_220k": None,
            "morph_radial_symmetry": None,
            "morph_convective_organization": None,
            "morph_eye_detected": False,
            "morph_eye_temperature_contrast": 0.0,
        }
