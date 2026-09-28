"""
Unit tests for spatial and temporal alignment engines.
"""

import numpy as np
import pytest

from ml.data.alignment.spatial import SpatialAligner
from ml.data.alignment.temporal import TemporalAligner
from ml.data.schemas.track import CycloneTrackPoint, CycloneTrackSeries


def test_temporal_alignment():
    series = CycloneTrackSeries(
        storm_id="TEST_ALIGN",
        storm_name="ALIGN_CYCLONE",
        season=2023,
        basin="NI",
        points=[
            CycloneTrackPoint(
                storm_id="TEST_ALIGN",
                storm_name="ALIGN_CYCLONE",
                season=2023,
                basin="NI",
                timestamp_utc="2023-05-12T00:00:00Z",
                latitude=10.0,
                longitude=80.0,
                wind_speed_kts=40.0,
            ),
            CycloneTrackPoint(
                storm_id="TEST_ALIGN",
                storm_name="ALIGN_CYCLONE",
                season=2023,
                basin="NI",
                timestamp_utc="2023-05-12T06:00:00Z",
                latitude=11.0,
                longitude=81.0,
                wind_speed_kts=50.0,
            ),
        ],
    )

    # 1. Exact match
    res_exact = TemporalAligner.align_observation_to_track("2023-05-12T06:00:00Z", series)
    assert res_exact.is_within_tolerance is True
    assert res_exact.time_difference_seconds == 0.0
    assert res_exact.matched_latitude == 11.0
    assert res_exact.matched_longitude == 81.0

    # 2. Linear interpolation between 00Z and 06Z at 03Z
    res_interp = TemporalAligner.align_observation_to_track("2023-05-12T03:00:00Z", series)
    assert res_interp.is_within_tolerance is True
    assert res_interp.is_interpolated is True
    assert abs(res_interp.matched_latitude - 10.5) < 1e-3
    assert abs(res_interp.matched_longitude - 80.5) < 1e-3
    assert abs(res_interp.matched_wind_kts - 45.0) < 1e-1

    # 3. Beyond tolerance (e.g. 10 hours later with tolerance=3h)
    res_out = TemporalAligner.align_observation_to_track(
        "2023-05-12T18:00:00Z", series, max_tolerance_hours=3.0
    )
    assert res_out.is_within_tolerance is False
    assert res_out.time_difference_hours == 12.0


def test_spatial_cyclone_centered_extraction():
    # 100x100 grid covering lat [10..20], lon [80..90]
    lats = np.linspace(10.0, 20.0, 100, dtype=np.float32)
    lons = np.linspace(80.0, 90.0, 100, dtype=np.float32)

    # Put a distinct signal at (lat 15.0, lon 85.0)
    grid = np.full((100, 100), 280.0, dtype=np.float32)
    grid[50, 50] = 190.0  # Cold eye center

    crop_arr, crop_meta = SpatialAligner.extract_crop(
        satellite_array=grid,
        lats=lats,
        lons=lons,
        center_lat=15.0,
        center_lon=85.0,
        crop_shape=(32, 32),
        pixel_resolution_deg=0.1,
        storm_id="TEST_CROP",
    )

    assert crop_arr.shape == (32, 32)
    assert crop_meta.crop_height == 32
    assert crop_meta.crop_width == 32
    # Verify center pixel is close to 190.0
    center_val = crop_arr[16, 16]
    assert center_val == 190.0
    assert crop_meta.is_boundary_padded is False


def test_spatial_crop_boundary_padding():
    lats = np.linspace(10.0, 20.0, 50, dtype=np.float32)
    lons = np.linspace(80.0, 90.0, 50, dtype=np.float32)
    grid = np.full((50, 50), 270.0, dtype=np.float32)

    # Center near corner boundary (lat 10.2, lon 80.2)
    crop_arr, crop_meta = SpatialAligner.extract_crop(
        satellite_array=grid,
        lats=lats,
        lons=lons,
        center_lat=10.2,
        center_lon=80.2,
        crop_shape=(32, 32),
        pixel_resolution_deg=0.1,
    )
    assert crop_meta.is_boundary_padded is True
    assert crop_meta.missing_pixels_count > 0
    assert np.isnan(crop_arr[0, 0])  # Out-of-bounds pixel is NaN
