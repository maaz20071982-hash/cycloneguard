"""
CycloneGuard Data Quality & Observational Completeness Features.

Quantifies the fidelity, temporal proximity, and completeness of multi-source inputs:
- Individual sensor availability flags (track, IR, ADT, INSAT, ASCAT, GMI)
- Spatio-temporal alignment error and gap
- Spatial boundary padding indicator
- Missing pixel fraction
- Overall data quality tier: GOOD, ACCEPTABLE, DEGRADED, INVALID
"""

from typing import Any, Dict, Optional


class QualityFeatureExtractor:
    """
    Evaluates observational quality and multi-source availability.
    """

    @classmethod
    def extract(
        cls,
        track_available: bool = False,
        ir_available: bool = False,
        adt_available: bool = False,
        insat_available: bool = False,
        scatterometer_available: bool = False,
        microwave_available: bool = False,
        temporal_gap_minutes: Optional[float] = None,
        is_boundary_padded: bool = False,
        missing_pixels_fraction: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Extract structured quality features and assign a scientific quality flag.
        """
        # Determine overall quality tier
        if not track_available and not ir_available:
            quality_flag = "INVALID"
        elif track_available and ir_available:
            gap = temporal_gap_minutes if temporal_gap_minutes is not None else 0.0
            if gap <= 90.0 and not is_boundary_padded and missing_pixels_fraction <= 0.01:
                quality_flag = "GOOD"
            elif gap <= 180.0 and missing_pixels_fraction <= 0.05:
                quality_flag = "ACCEPTABLE"
            else:
                quality_flag = "DEGRADED"
        elif track_available and not ir_available:
            # Track-only state (no coincident satellite image)
            quality_flag = "PARTIAL_TRACK_ONLY"
        else:
            quality_flag = "DEGRADED"

        return {
            "quality_track_available": track_available,
            "quality_ir_available": ir_available,
            "quality_adt_available": adt_available,
            "quality_insat_available": insat_available,
            "quality_scatterometer_available": scatterometer_available,
            "quality_microwave_available": microwave_available,
            "quality_temporal_gap_minutes": round(temporal_gap_minutes, 1) if temporal_gap_minutes is not None else None,
            "quality_is_boundary_padded": is_boundary_padded,
            "quality_missing_pixels_fraction": round(missing_pixels_fraction, 4),
            "quality_overall_flag": quality_flag,
        }
