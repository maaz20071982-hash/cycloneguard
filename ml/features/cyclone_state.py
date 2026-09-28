"""
CycloneGuard Cyclone State Representation & Builder.

Transforms heterogeneous multi-source observations at a specific time step
into a standardized, scientifically inspectable CycloneState object.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from ml.data.schemas.track import CycloneTrackPoint, CycloneTrackSeries
from ml.data.schemas.satellite import CycloneCenteredCrop
from ml.features.track_features import TrackFeatureExtractor
from ml.features.satellite_features import SatelliteFeatureExtractor
from ml.features.temporal_features import TemporalFeatureExtractor
from ml.features.cross_source import CrossSourceConsistencyEngine
from ml.features.quality_features import QualityFeatureExtractor


class CycloneLocation(BaseModel):
    """Geographic position of cyclone center."""
    latitude: float
    longitude: float


class CycloneIntensity(BaseModel):
    """Intensity measurement metadata."""
    value: Optional[float] = None
    unit: str = "knots"
    source: str = "noaa_ibtracs"
    central_pressure_mb: Optional[float] = None


class CycloneState(BaseModel):
    """
    Standardized, multi-source state representation of a tropical cyclone at timestamp t0.
    """
    storm_id: str
    storm_name: Optional[str] = None
    timestamp_utc: str
    location: CycloneLocation
    intensity: CycloneIntensity

    # Feature groups
    track_features: Dict[str, Any] = Field(default_factory=dict)
    satellite_features: Dict[str, Any] = Field(default_factory=dict)
    morphology_features: Dict[str, Any] = Field(default_factory=dict)
    temporal_features: Dict[str, Any] = Field(default_factory=dict)
    cross_source_features: Dict[str, Any] = Field(default_factory=dict)
    data_quality: Dict[str, Any] = Field(default_factory=dict)

    # Provenance and source availability lists
    available_sources: List[str] = Field(default_factory=list)
    missing_sources: List[str] = Field(default_factory=list)
    schema_version: str = "state_schema_v1"

    def get_all_features_flat(self) -> Dict[str, Any]:
        """Return a single flattened dictionary of all feature keys and values."""
        flat: Dict[str, Any] = {}
        flat.update(self.track_features)
        flat.update(self.satellite_features)
        flat.update(self.morphology_features)
        flat.update(self.temporal_features)
        flat.update(self.cross_source_features)
        flat.update(self.data_quality)
        return flat


class CycloneStateBuilder:
    """
    Assembles a complete, validated CycloneState object from observational streams.
    """

    @classmethod
    def build_state(
        cls,
        current_track: CycloneTrackPoint,
        previous_track: Optional[CycloneTrackPoint] = None,
        hist_6h_track: Optional[CycloneTrackPoint] = None,
        hist_12h_track: Optional[CycloneTrackPoint] = None,
        satellite_crop: Optional[CycloneCenteredCrop] = None,
        hist_6h_satellite_crop: Optional[CycloneCenteredCrop] = None,
        adt_wind_kts: Optional[float] = None,
    ) -> CycloneState:
        """
        Assemble a CycloneState for the given track point and observational inputs.
        """
        available_sources: List[str] = []
        missing_sources: List[str] = [
            "isro_insat3d_mosdac",
            "eumetsat_ascat",
            "gpm_gmi_microwave",
        ]

        # 1. Track Features
        available_sources.append("noaa_ibtracs")
        track_feats = TrackFeatureExtractor.extract(current_track, previous_track)

        # 2. Satellite & Morphology Features
        sat_feats: Dict[str, Any] = {}
        morph_feats: Dict[str, Any] = {}
        curr_ir_min: Optional[float] = None
        missing_pixels_frac = 0.0
        is_padded = False
        temporal_gap_min = 0.0

        if satellite_crop is not None:
            available_sources.append("noaa_hursat_b1")
            ir_array = satellite_crop.crop_array
            missing_pixels_frac = satellite_crop.missing_pixels_fraction
            is_padded = satellite_crop.is_boundary_padded

            all_sat_morph = SatelliteFeatureExtractor.extract_from_crop(
                ir_array=ir_array,
                pixel_resolution_deg=satellite_crop.pixel_resolution_deg,
            )
            # Separate sat vs morph keys
            sat_keys = {
                "sat_ir_min_temp", "sat_ir_mean_temp", "sat_ir_std_temp",
                "sat_ir_p10_temp", "sat_ir_p50_temp", "sat_ir_core_temp",
                "sat_ir_ring_temp", "sat_ir_eye_surround_diff",
                "sat_cold_cloud_fraction_200k", "sat_cold_cloud_fraction_210k",
                "sat_cold_cloud_fraction_220k",
            }
            morph_keys = {
                "morph_radial_symmetry", "morph_convective_organization",
                "morph_eye_detected", "morph_eye_temperature_contrast",
            }
            sat_feats = {k: v for k, v in all_sat_morph.items() if k in sat_keys}
            morph_feats = {k: v for k, v in all_sat_morph.items() if k in morph_keys}
            curr_ir_min = sat_feats.get("sat_ir_min_temp")

            # Temporal gap
            sat_dt = datetime.fromisoformat(satellite_crop.observation_time_utc.replace("Z", "+00:00"))
            track_dt = datetime.fromisoformat(str(current_track.timestamp_utc).replace("Z", "+00:00"))
            temporal_gap_min = abs((track_dt - sat_dt).total_seconds()) / 60.0
        else:
            missing_sources.append("noaa_hursat_b1")
            empty_sat = SatelliteFeatureExtractor._empty_features()
            sat_feats = {k: empty_sat[k] for k in empty_sat if k.startswith("sat_")}
            morph_feats = {k: empty_sat[k] for k in empty_sat if k.startswith("morph_")}

        # 3. Temporal Features
        hist_6h_ir_min: Optional[float] = None
        if hist_6h_satellite_crop is not None:
            hist_extracted = SatelliteFeatureExtractor.extract_from_crop(hist_6h_satellite_crop.crop_array)
            hist_6h_ir_min = hist_extracted.get("sat_ir_min_temp")

        temp_feats = TemporalFeatureExtractor.extract(
            current_time_utc=current_track.timestamp_utc,
            current_wind_kts=current_track.wind_speed_kts,
            current_pressure_mb=current_track.central_pressure_mb,
            current_ir_min_k=curr_ir_min,
            hist_6h_time_utc=hist_6h_track.timestamp_utc if hist_6h_track else None,
            hist_6h_wind_kts=hist_6h_track.wind_speed_kts if hist_6h_track else None,
            hist_6h_pressure_mb=hist_6h_track.central_pressure_mb if hist_6h_track else None,
            hist_6h_ir_min_k=hist_6h_ir_min,
            hist_12h_time_utc=hist_12h_track.timestamp_utc if hist_12h_track else None,
            hist_12h_wind_kts=hist_12h_track.wind_speed_kts if hist_12h_track else None,
        )

        # 4. Cross-Source Consistency Features
        if adt_wind_kts is not None:
            available_sources.append("noaa_adt_hursat")
        else:
            missing_sources.append("noaa_adt_hursat")

        cross_feats = CrossSourceConsistencyEngine.evaluate(
            track_wind_kts=current_track.wind_speed_kts,
            adt_wind_kts=adt_wind_kts,
            sat_cold_cloud_frac_210k=sat_feats.get("sat_cold_cloud_fraction_210k"),
        )

        # 5. Data Quality Features
        quality_feats = QualityFeatureExtractor.extract(
            track_available=True,
            ir_available=(satellite_crop is not None),
            adt_available=(adt_wind_kts is not None),
            insat_available=False,
            scatterometer_available=False,
            microwave_available=False,
            temporal_gap_minutes=temporal_gap_min if satellite_crop is not None else None,
            is_boundary_padded=is_padded,
            missing_pixels_fraction=missing_pixels_frac,
        )

        return CycloneState(
            storm_id=current_track.storm_id,
            storm_name=current_track.storm_name,
            timestamp_utc=str(current_track.timestamp_utc),
            location=CycloneLocation(
                latitude=current_track.latitude,
                longitude=current_track.longitude,
            ),
            intensity=CycloneIntensity(
                value=current_track.wind_speed_kts,
                unit="knots",
                source="noaa_ibtracs",
                central_pressure_mb=current_track.central_pressure_mb,
            ),
            track_features=track_feats,
            satellite_features=sat_feats,
            morphology_features=morph_feats,
            temporal_features=temp_feats,
            cross_source_features=cross_feats,
            data_quality=quality_feats,
            available_sources=available_sources,
            missing_sources=missing_sources,
            schema_version="state_schema_v1",
        )
