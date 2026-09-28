"""
Unit tests for CycloneGuard Feature Registry and Extractors.
Verifies Phase 2 to 7 of Sprint 5:
- Feature Registry
- Track Features (TrackFeatureExtractor)
- Satellite Features (SatelliteFeatureExtractor)
- Temporal Features (TemporalFeatureExtractor)
- Cross-Source Consistency (CrossSourceConsistencyEngine)
- Data Quality & Missingness Indicators (QualityFeatureExtractor)
"""

import numpy as np
import pytest

from ml.features.registry import FeatureRegistry, FeatureCategory
from ml.features.track_features import TrackFeatureExtractor
from ml.features.satellite_features import SatelliteFeatureExtractor
from ml.features.temporal_features import TemporalFeatureExtractor
from ml.features.cross_source import CrossSourceConsistencyEngine
from ml.features.quality_features import QualityFeatureExtractor
from ml.data.schemas.track import CycloneTrackPoint


def test_feature_registry_lookup():
    """Verify registry catalogs features with units, sources, and categories."""
    reg = FeatureRegistry()
    assert len(reg.list_all()) >= 35
    
    # Retrieve specific features
    f_wind = reg.get("track_wind_speed")
    assert f_wind is not None
    assert f_wind.unit == "knots"
    assert f_wind.source == "noaa_ibtracs"
    assert f_wind.category == FeatureCategory.TRACK
    
    f_eye = reg.get("morph_eye_detected")
    assert f_eye is not None
    assert f_eye.unit == "boolean"
    assert f_eye.category == FeatureCategory.MORPHOLOGY
    
    # Filter by category
    quality_feats = reg.get_by_category(FeatureCategory.DATA_QUALITY)
    assert len(quality_feats) >= 5


def test_track_feature_extraction():
    """Verify motion calculation, great circle distance, and forward bearing."""
    pt1 = CycloneTrackPoint(
        storm_id="TEST_STORM",
        storm_name="TEST",
        season=2023,
        basin="NI",
        timestamp_utc="2023-05-10T00:00:00Z",
        latitude=10.0,
        longitude=85.0,
        wind_speed_kts=35.0,
        central_pressure_mb=996.0,
    )
    pt2 = CycloneTrackPoint(
        storm_id="TEST_STORM",
        storm_name="TEST",
        season=2023,
        basin="NI",
        timestamp_utc="2023-05-10T06:00:00Z",
        latitude=11.0,
        longitude=85.5,
        wind_speed_kts=45.0,
        central_pressure_mb=990.0,
    )

    feats = TrackFeatureExtractor.extract(current_point=pt2, previous_point=pt1)
    
    assert feats["track_latitude"] == 11.0
    assert feats["track_longitude"] == 85.5
    assert feats["track_wind_speed"] == 45.0
    assert feats["track_pressure"] == 990.0
    
    # Motion calculations
    assert feats["track_translation_speed_kts"] is not None
    assert feats["track_translation_speed_kts"] > 5.0
    assert feats["track_translation_bearing_deg"] is not None
    assert 0 <= feats["track_translation_bearing_deg"] <= 360


def test_satellite_feature_extraction_synthetic_patch():
    """Verify statistical and morphological extraction from 2D IR patch."""
    # Synthetic warm eye (250K) surrounded by cold convective ring (195K)
    grid = np.full((101, 101), 260.0, dtype=np.float32)
    y, x = np.ogrid[:101, :101]
    dist_from_center = np.sqrt((x - 50)**2 + (y - 50)**2)
    
    # Dense cold ring between r=8 and r=25
    cold_ring = (dist_from_center >= 8) & (dist_from_center <= 25)
    grid[cold_ring] = 195.0
    
    # Warm eye at center r < 6
    eye_mask = dist_from_center < 6
    grid[eye_mask] = 245.0

    feats = SatelliteFeatureExtractor.extract_from_crop(grid)
    
    assert feats["sat_ir_min_temp"] == pytest.approx(195.0, abs=1.0)
    assert feats["sat_cold_cloud_fraction_200k"] > 0.05
    assert feats["sat_cold_cloud_fraction_220k"] > 0.10
    assert feats["sat_ir_eye_surround_diff"] is not None
    assert feats["sat_ir_eye_surround_diff"] > 20.0  # Warm eye warmer than cold ring
    assert feats["morph_radial_symmetry"] is not None
    assert feats["morph_radial_symmetry"] > 0.80  # Circular symmetry is high
    assert feats["morph_eye_detected"] is True  # Algorithmic eye detection detects eye


def test_temporal_feature_extraction():
    """Verify delta wind, delta pressure, and change rates."""
    t_curr = "2023-05-10T06:00:00Z"
    t_6h = "2023-05-10T00:00:00Z"

    feats = TemporalFeatureExtractor.extract(
        current_time_utc=t_curr,
        current_wind_kts=55.0,
        current_pressure_mb=980.0,
        current_ir_min_k=198.0,
        hist_6h_time_utc=t_6h,
        hist_6h_wind_kts=40.0,
        hist_6h_pressure_mb=990.0,
        hist_6h_ir_min_k=205.0,
    )
    
    assert feats["temp_delta_wind_6h"] == 15.0
    assert feats["temp_delta_pressure_6h"] == -10.0
    assert feats["temp_wind_change_rate_per_hour"] == pytest.approx(2.5, abs=0.1)
    assert feats["temp_delta_ir_min_6h"] == -7.0


def test_cross_source_consistency_when_sources_missing():
    """Verify scientifically honest behavior: report insufficient evidence when multi-source pairs absent."""
    cs = CrossSourceConsistencyEngine.evaluate(track_wind_kts=50.0, adt_wind_kts=None)
    assert cs["cross_intensity_agreement"] == "insufficient_evidence"
    assert cs["cross_adt_track_diff_kts"] is None


def test_data_quality_evaluation():
    """Verify data quality flags reflect sensor coverage and observation validity."""
    q_track_only = QualityFeatureExtractor.extract(
        track_available=True,
        ir_available=False,
    )
    assert q_track_only["quality_track_available"] is True
    assert q_track_only["quality_ir_available"] is False
    assert q_track_only["quality_overall_flag"] == "PARTIAL_TRACK_ONLY"

    q_full = QualityFeatureExtractor.extract(
        track_available=True,
        ir_available=True,
        temporal_gap_minutes=15.0,
        is_boundary_padded=False,
        missing_pixels_fraction=0.0,
    )
    assert q_full["quality_overall_flag"] == "GOOD"
