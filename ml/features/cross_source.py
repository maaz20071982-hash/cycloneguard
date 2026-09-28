"""
CycloneGuard Cross-Source Consistency Engine.

Evaluates scientific consistency across independent observational streams
where compatible physical quantities exist:
- ADT objective intensity vs. IBTrACS ground truth intensity (kts)
- IR convective coverage vs. reported intensity physical plausibility
- Returns 'insufficient_evidence' when multi-source pairs are unavailable
"""

from typing import Any, Dict, Optional


class CrossSourceConsistencyEngine:
    """
    Evaluates physical consistency between multi-sensor cyclone observations.
    Never compares incompatible dimensions or fabricates consensus.
    """

    @classmethod
    def evaluate(
        cls,
        track_wind_kts: Optional[float] = None,
        adt_wind_kts: Optional[float] = None,
        sat_cold_cloud_frac_210k: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate cross-source consistency.
        """
        features: Dict[str, Any] = {
            "cross_intensity_agreement": "insufficient_evidence",
            "cross_adt_track_diff_kts": None,
            "cross_convection_wind_plausibility": None,
        }

        # 1. ADT vs. Best-Track Wind Comparison
        if track_wind_kts is not None and adt_wind_kts is not None:
            diff_kts = adt_wind_kts - track_wind_kts
            features["cross_adt_track_diff_kts"] = round(diff_kts, 1)

            abs_diff = abs(diff_kts)
            if abs_diff <= 10.0:
                features["cross_intensity_agreement"] = "consistent"
            elif abs_diff <= 20.0:
                features["cross_intensity_agreement"] = "partially_consistent"
            else:
                features["cross_intensity_agreement"] = "disagreeing"
        else:
            features["cross_intensity_agreement"] = "insufficient_evidence"

        # 2. Convection-Wind Physical Plausibility Score
        if track_wind_kts is not None and sat_cold_cloud_frac_210k is not None:
            # Physics heuristic: High winds (>=65 kts) typically correspond to substantial cold cloud tops (frac >= 0.05)
            # Low winds (<=30 kts) with zero cold cloud tops is completely plausible.
            if track_wind_kts >= 65.0:
                if sat_cold_cloud_frac_210k >= 0.05:
                    plausibility = 1.0
                elif sat_cold_cloud_frac_210k >= 0.01:
                    plausibility = 0.7
                else:
                    plausibility = 0.3  # Possible severe shear or uncalibrated raster
            elif track_wind_kts >= 45.0:
                plausibility = 0.9 if sat_cold_cloud_frac_210k >= 0.01 else 0.6
            else:
                plausibility = 1.0  # Weak system, convective coverage varies naturally

            features["cross_convection_wind_plausibility"] = round(plausibility, 2)

        return features
