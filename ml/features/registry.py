"""
CycloneGuard Centralized Feature Registry.

Stores, validates, and provides versioned feature definitions.
Every feature in the AI pipeline must be registered here with:
- Unique name
- Scientific category
- Data type
- Provider source
- Source variable
- Physical units
- Documented description
"""

from typing import Dict, List, Optional
from ml.features.base import FeatureCategory, FeatureDefinition, FeatureType


class FeatureRegistry:
    """
    Central registry singleton for engineered meteorological features.
    """
    def __init__(self):
        self._features: Dict[str, FeatureDefinition] = {}
        self._register_default_features()

    def register(self, feature: FeatureDefinition) -> None:
        """Register a feature definition. Disallows duplicate names."""
        if feature.name in self._features:
            raise ValueError(f"Feature '{feature.name}' is already registered.")
        self._features[feature.name] = feature

    def get(self, name: str) -> Optional[FeatureDefinition]:
        """Retrieve a feature definition by name."""
        return self._features.get(name)

    def list_all(self) -> List[FeatureDefinition]:
        """Return all registered features in deterministic registration order."""
        return list(self._features.values())

    def get_by_category(self, category: FeatureCategory) -> List[FeatureDefinition]:
        """Return all features belonging to a specific scientific category."""
        return [f for f in self._features.values() if f.category == category]

    def get_numerical_feature_names(self) -> List[str]:
        """Return names of numerical features suitable for state vectors."""
        return [
            f.name for f in self._features.values()
            if f.feature_type in (FeatureType.NUMERICAL, FeatureType.BOOLEAN)
        ]

    def _register_default_features(self) -> None:
        """Register all validated Sprint 5 features supported by actual data."""

        # ---------------------------------------------------------------------
        # 1. TRACK & INTENSITY FEATURES (Source: noaa_ibtracs)
        # ---------------------------------------------------------------------
        self.register(FeatureDefinition(
            name="track_latitude",
            category=FeatureCategory.TRACK,
            feature_type=FeatureType.NUMERICAL,
            source="noaa_ibtracs",
            variable="LAT",
            unit="degrees_north",
            description="Cyclone center latitude coordinate",
            is_raw=True,
            valid_range_min=-90.0,
            valid_range_max=90.0,
        ))
        self.register(FeatureDefinition(
            name="track_longitude",
            category=FeatureCategory.TRACK,
            feature_type=FeatureType.NUMERICAL,
            source="noaa_ibtracs",
            variable="LON",
            unit="degrees_east",
            description="Cyclone center longitude coordinate normalized to [-180, 180]",
            is_raw=True,
            valid_range_min=-180.0,
            valid_range_max=180.0,
        ))
        self.register(FeatureDefinition(
            name="track_wind_speed",
            category=FeatureCategory.TRACK,
            feature_type=FeatureType.NUMERICAL,
            source="noaa_ibtracs",
            variable="WMO_WIND",
            unit="knots",
            description="Maximum 10-minute (or agency reported) sustained surface wind speed",
            is_raw=True,
            valid_range_min=0.0,
            valid_range_max=250.0,
        ))
        self.register(FeatureDefinition(
            name="track_pressure",
            category=FeatureCategory.TRACK,
            feature_type=FeatureType.NUMERICAL,
            source="noaa_ibtracs",
            variable="WMO_PRES",
            unit="mb",
            description="Minimum central atmospheric surface pressure",
            is_raw=True,
            valid_range_min=850.0,
            valid_range_max=1050.0,
        ))
        self.register(FeatureDefinition(
            name="track_translation_speed_kts",
            category=FeatureCategory.TRACK,
            feature_type=FeatureType.NUMERICAL,
            source="noaa_ibtracs",
            variable="DERIVED_SPEED",
            unit="knots",
            description="Cyclone forward motion speed computed from displacement over previous 6 hours",
            is_raw=False,
            valid_range_min=0.0,
            valid_range_max=80.0,
        ))
        self.register(FeatureDefinition(
            name="track_translation_bearing_deg",
            category=FeatureCategory.TRACK,
            feature_type=FeatureType.NUMERICAL,
            source="noaa_ibtracs",
            variable="DERIVED_BEARING",
            unit="degrees",
            description="Compass bearing of cyclone forward motion vector (0-360 degrees clockwise from north)",
            is_raw=False,
            valid_range_min=0.0,
            valid_range_max=360.0,
        ))

        # ---------------------------------------------------------------------
        # 2. SATELLITE SPATIAL FEATURES (Source: noaa_hursat_b1)
        # ---------------------------------------------------------------------
        self.register(FeatureDefinition(
            name="sat_ir_min_temp",
            category=FeatureCategory.SATELLITE_RAW,
            feature_type=FeatureType.NUMERICAL,
            source="noaa_hursat_b1",
            variable="IRWIN",
            unit="Kelvin",
            description="Minimum IR window brightness temperature across storm domain (deepest convection)",
            is_raw=True,
            valid_range_min=160.0,
            valid_range_max=320.0,
        ))
        self.register(FeatureDefinition(
            name="sat_ir_mean_temp",
            category=FeatureCategory.SATELLITE_DERIVED,
            feature_type=FeatureType.NUMERICAL,
            source="noaa_hursat_b1",
            variable="IRWIN",
            unit="Kelvin",
            description="Spatial mean IR window brightness temperature across storm crop",
            is_raw=False,
            valid_range_min=180.0,
            valid_range_max=320.0,
        ))
        self.register(FeatureDefinition(
            name="sat_ir_std_temp",
            category=FeatureCategory.SATELLITE_DERIVED,
            feature_type=FeatureType.NUMERICAL,
            source="noaa_hursat_b1",
            variable="IRWIN",
            unit="Kelvin",
            description="Spatial standard deviation of IR window brightness temperature",
            is_raw=False,
            valid_range_min=0.0,
            valid_range_max=60.0,
        ))
        self.register(FeatureDefinition(
            name="sat_ir_core_temp",
            category=FeatureCategory.SATELLITE_DERIVED,
            feature_type=FeatureType.NUMERICAL,
            source="noaa_hursat_b1",
            variable="IRWIN",
            unit="Kelvin",
            description="Mean brightness temperature in inner core radius (r <= 50 km)",
            is_raw=False,
            valid_range_min=170.0,
            valid_range_max=320.0,
        ))
        self.register(FeatureDefinition(
            name="sat_ir_ring_temp",
            category=FeatureCategory.SATELLITE_DERIVED,
            feature_type=FeatureType.NUMERICAL,
            source="noaa_hursat_b1",
            variable="IRWIN",
            unit="Kelvin",
            description="Mean brightness temperature in surrounding eyewall ring (50 km < r <= 150 km)",
            is_raw=False,
            valid_range_min=170.0,
            valid_range_max=320.0,
        ))
        self.register(FeatureDefinition(
            name="sat_ir_eye_surround_diff",
            category=FeatureCategory.SATELLITE_DERIVED,
            feature_type=FeatureType.NUMERICAL,
            source="noaa_hursat_b1",
            variable="IRWIN",
            unit="Kelvin",
            description="Thermal contrast between inner core and eyewall ring (T_core - T_ring)",
            is_raw=False,
            valid_range_min=-50.0,
            valid_range_max=50.0,
        ))
        self.register(FeatureDefinition(
            name="sat_cold_cloud_fraction_200k",
            category=FeatureCategory.SATELLITE_DERIVED,
            feature_type=FeatureType.NUMERICAL,
            source="noaa_hursat_b1",
            variable="IRWIN",
            unit="fraction",
            description="Fraction of pixels with brightness temperature < 200 K (extreme overshooting convection)",
            is_raw=False,
            valid_range_min=0.0,
            valid_range_max=1.0,
        ))
        self.register(FeatureDefinition(
            name="sat_cold_cloud_fraction_210k",
            category=FeatureCategory.SATELLITE_DERIVED,
            feature_type=FeatureType.NUMERICAL,
            source="noaa_hursat_b1",
            variable="IRWIN",
            unit="fraction",
            description="Fraction of pixels with brightness temperature < 210 K (severe convection)",
            is_raw=False,
            valid_range_min=0.0,
            valid_range_max=1.0,
        ))
        self.register(FeatureDefinition(
            name="sat_cold_cloud_fraction_220k",
            category=FeatureCategory.SATELLITE_DERIVED,
            feature_type=FeatureType.NUMERICAL,
            source="noaa_hursat_b1",
            variable="IRWIN",
            unit="fraction",
            description="Fraction of pixels with brightness temperature < 220 K (convective cloud shield)",
            is_raw=False,
            valid_range_min=0.0,
            valid_range_max=1.0,
        ))

        # ---------------------------------------------------------------------
        # 3. MORPHOLOGY FEATURES
        # ---------------------------------------------------------------------
        self.register(FeatureDefinition(
            name="morph_radial_symmetry",
            category=FeatureCategory.MORPHOLOGY,
            feature_type=FeatureType.NUMERICAL,
            source="noaa_hursat_b1",
            variable="DERIVED_SYMMETRY",
            unit="dimensionless",
            description="Azimuthal symmetry score computed from angular variance in radial bins (0.0=asymmetric, 1.0=circular)",
            is_raw=False,
            valid_range_min=0.0,
            valid_range_max=1.0,
        ))
        self.register(FeatureDefinition(
            name="morph_convective_organization",
            category=FeatureCategory.MORPHOLOGY,
            feature_type=FeatureType.NUMERICAL,
            source="noaa_hursat_b1",
            variable="DERIVED_CONVECTION",
            unit="dimensionless",
            description="Ratio of inner-core deep convection (<210K within 100km) to total domain deep convection",
            is_raw=False,
            valid_range_min=0.0,
            valid_range_max=1.0,
        ))
        self.register(FeatureDefinition(
            name="morph_eye_detected",
            category=FeatureCategory.MORPHOLOGY,
            feature_type=FeatureType.BOOLEAN,
            source="noaa_hursat_b1",
            variable="DERIVED_EYE",
            unit="boolean",
            description="Flag indicating whether a closed warm core feature surrounded by cold cloud was algorithmically detected",
            is_raw=False,
        ))
        self.register(FeatureDefinition(
            name="morph_eye_temperature_contrast",
            category=FeatureCategory.MORPHOLOGY,
            feature_type=FeatureType.NUMERICAL,
            source="noaa_hursat_b1",
            variable="DERIVED_EYE_CONTRAST",
            unit="Kelvin",
            description="Warm eye temperature minus cold eyewall boundary if eye detected, else 0.0",
            is_raw=False,
            valid_range_min=0.0,
            valid_range_max=50.0,
        ))

        # ---------------------------------------------------------------------
        # 4. TEMPORAL DYNAMICS FEATURES
        # ---------------------------------------------------------------------
        self.register(FeatureDefinition(
            name="temp_delta_wind_6h",
            category=FeatureCategory.TEMPORAL,
            feature_type=FeatureType.NUMERICAL,
            source="noaa_ibtracs",
            variable="WMO_WIND",
            unit="knots",
            description="Change in maximum sustained wind speed over previous 6 hours (V_t0 - V_t-6h)",
            is_raw=False,
            valid_range_min=-100.0,
            valid_range_max=100.0,
        ))
        self.register(FeatureDefinition(
            name="temp_delta_wind_12h",
            category=FeatureCategory.TEMPORAL,
            feature_type=FeatureType.NUMERICAL,
            source="noaa_ibtracs",
            variable="WMO_WIND",
            unit="knots",
            description="Change in maximum sustained wind speed over previous 12 hours (V_t0 - V_t-12h)",
            is_raw=False,
            valid_range_min=-120.0,
            valid_range_max=120.0,
        ))
        self.register(FeatureDefinition(
            name="temp_delta_pressure_6h",
            category=FeatureCategory.TEMPORAL,
            feature_type=FeatureType.NUMERICAL,
            source="noaa_ibtracs",
            variable="WMO_PRES",
            unit="mb",
            description="Change in central pressure over previous 6 hours (P_t0 - P_t-6h)",
            is_raw=False,
            valid_range_min=-80.0,
            valid_range_max=80.0,
        ))
        self.register(FeatureDefinition(
            name="temp_wind_change_rate_per_hour",
            category=FeatureCategory.TEMPORAL,
            feature_type=FeatureType.NUMERICAL,
            source="noaa_ibtracs",
            variable="DERIVED_V_RATE",
            unit="knots_per_hour",
            description="Instantaneous rate of wind speed change per elapsed hour",
            is_raw=False,
            valid_range_min=-15.0,
            valid_range_max=15.0,
        ))
        self.register(FeatureDefinition(
            name="temp_delta_ir_min_6h",
            category=FeatureCategory.TEMPORAL,
            feature_type=FeatureType.NUMERICAL,
            source="noaa_hursat_b1",
            variable="IRWIN",
            unit="Kelvin",
            description="Change in minimum IR brightness temperature over previous 6 hours (cooling indicates deepening)",
            is_raw=False,
            valid_range_min=-80.0,
            valid_range_max=80.0,
        ))

        # ---------------------------------------------------------------------
        # 5. CROSS-SOURCE CONSISTENCY FEATURES
        # ---------------------------------------------------------------------
        self.register(FeatureDefinition(
            name="cross_intensity_agreement",
            category=FeatureCategory.CROSS_SOURCE,
            feature_type=FeatureType.CATEGORICAL,
            source="multi_source",
            variable="CONSISTENCY_STATUS",
            unit="status",
            description="Agreement status between independent intensity sources: consistent, partially_consistent, disagreeing, insufficient_evidence",
            is_raw=False,
        ))
        self.register(FeatureDefinition(
            name="cross_adt_track_diff_kts",
            category=FeatureCategory.CROSS_SOURCE,
            feature_type=FeatureType.NUMERICAL,
            source="noaa_adt_hursat",
            variable="WIND_DIFF",
            unit="knots",
            description="Difference between ADT objective intensity and IBTrACS best-track wind speed (V_adt - V_track)",
            is_raw=False,
            valid_range_min=-80.0,
            valid_range_max=80.0,
        ))
        self.register(FeatureDefinition(
            name="cross_convection_wind_plausibility",
            category=FeatureCategory.CROSS_SOURCE,
            feature_type=FeatureType.NUMERICAL,
            source="multi_source",
            variable="PLAUSIBILITY_SCORE",
            unit="score",
            description="Physical plausibility score (0.0 to 1.0) relating cold cloud coverage to current wind speed",
            is_raw=False,
            valid_range_min=0.0,
            valid_range_max=1.0,
        ))

        # ---------------------------------------------------------------------
        # 6. DATA QUALITY & SENSOR AVAILABILITY FEATURES
        # ---------------------------------------------------------------------
        self.register(FeatureDefinition(
            name="quality_track_available",
            category=FeatureCategory.DATA_QUALITY,
            feature_type=FeatureType.BOOLEAN,
            source="noaa_ibtracs",
            variable="AVAILABILITY",
            unit="boolean",
            description="Flag indicating best-track coordinates and intensity were available at t0",
            is_raw=False,
        ))
        self.register(FeatureDefinition(
            name="quality_ir_available",
            category=FeatureCategory.DATA_QUALITY,
            feature_type=FeatureType.BOOLEAN,
            source="noaa_hursat_b1",
            variable="AVAILABILITY",
            unit="boolean",
            description="Flag indicating satellite IR window imagery was available and aligned at t0",
            is_raw=False,
        ))
        self.register(FeatureDefinition(
            name="quality_adt_available",
            category=FeatureCategory.DATA_QUALITY,
            feature_type=FeatureType.BOOLEAN,
            source="noaa_adt_hursat",
            variable="AVAILABILITY",
            unit="boolean",
            description="Flag indicating ADT reanalysis was available at t0",
            is_raw=False,
        ))
        self.register(FeatureDefinition(
            name="quality_insat_available",
            category=FeatureCategory.DATA_QUALITY,
            feature_type=FeatureType.BOOLEAN,
            source="isro_insat3d_mosdac",
            variable="AVAILABILITY",
            unit="boolean",
            description="Flag indicating ISRO INSAT-3D/3DR observations were available at t0",
            is_raw=False,
        ))
        self.register(FeatureDefinition(
            name="quality_scatterometer_available",
            category=FeatureCategory.DATA_QUALITY,
            feature_type=FeatureType.BOOLEAN,
            source="eumetsat_ascat",
            variable="AVAILABILITY",
            unit="boolean",
            description="Flag indicating ocean vector wind scatterometer observations were available at t0",
            is_raw=False,
        ))
        self.register(FeatureDefinition(
            name="quality_microwave_available",
            category=FeatureCategory.DATA_QUALITY,
            feature_type=FeatureType.BOOLEAN,
            source="gpm_gmi_microwave",
            variable="AVAILABILITY",
            unit="boolean",
            description="Flag indicating passive microwave observations were available at t0",
            is_raw=False,
        ))
        self.register(FeatureDefinition(
            name="quality_temporal_gap_minutes",
            category=FeatureCategory.DATA_QUALITY,
            feature_type=FeatureType.NUMERICAL,
            source="alignment_engine",
            variable="DELTA_T",
            unit="minutes",
            description="Absolute time gap between satellite scan and matched best-track observation",
            is_raw=False,
            valid_range_min=0.0,
            valid_range_max=720.0,
        ))
        self.register(FeatureDefinition(
            name="quality_is_boundary_padded",
            category=FeatureCategory.DATA_QUALITY,
            feature_type=FeatureType.BOOLEAN,
            source="spatial_engine",
            variable="IS_PADDED",
            unit="boolean",
            description="Flag indicating cyclone crop intersected satellite domain boundary and was padded",
            is_raw=False,
        ))
        self.register(FeatureDefinition(
            name="quality_missing_pixels_fraction",
            category=FeatureCategory.DATA_QUALITY,
            feature_type=FeatureType.NUMERICAL,
            source="spatial_engine",
            variable="MISSING_FRACTION",
            unit="fraction",
            description="Fraction of missing/fill pixels in the cyclone-centered crop",
            is_raw=False,
            valid_range_min=0.0,
            valid_range_max=1.0,
        ))
        self.register(FeatureDefinition(
            name="quality_overall_flag",
            category=FeatureCategory.DATA_QUALITY,
            feature_type=FeatureType.QUALITY_FLAG,
            source="quality_engine",
            variable="QUALITY_FLAG",
            unit="flag",
            description="Comprehensive quality tier: GOOD, ACCEPTABLE, DEGRADED, INVALID",
            is_raw=False,
        ))


# Global default instance
GLOBAL_FEATURE_REGISTRY = FeatureRegistry()
