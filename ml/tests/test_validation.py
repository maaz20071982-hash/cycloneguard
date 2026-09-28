"""
Unit tests for data validation engine.
"""

import numpy as np
import pytest

from ml.data.schemas.adapter_results import ValidationSeverity
from ml.data.schemas.track import CycloneTrackPoint, CycloneTrackSeries
from ml.data.validation.validator import DataValidator


def test_validate_track_series_valid():
    series = CycloneTrackSeries(
        storm_id="TEST01",
        storm_name="TEST_STORM",
        season=2023,
        basin="NI",
        points=[
            CycloneTrackPoint(
                storm_id="TEST01",
                storm_name="TEST_STORM",
                season=2023,
                basin="NI",
                timestamp_utc="2023-05-10T00:00:00Z",
                latitude=12.0,
                longitude=85.0,
                wind_speed_kts=45.0,
                central_pressure_mb=996.0,
            ),
            CycloneTrackPoint(
                storm_id="TEST01",
                storm_name="TEST_STORM",
                season=2023,
                basin="NI",
                timestamp_utc="2023-05-10T06:00:00Z",
                latitude=12.5,
                longitude=85.2,
                wind_speed_kts=55.0,
                central_pressure_mb=988.0,
            ),
        ],
    )
    rep = DataValidator.validate_track_series(series)
    assert rep.status == ValidationSeverity.VALID
    assert rep.is_valid is True


def test_validate_track_series_invalid_coordinates():
    series = CycloneTrackSeries(
        storm_id="TEST02",
        storm_name="BAD_COORDS",
        season=2023,
        basin="NI",
        points=[
            CycloneTrackPoint(
                storm_id="TEST02",
                storm_name="BAD_COORDS",
                season=2023,
                basin="NI",
                timestamp_utc="2023-05-10T00:00:00Z",
                latitude=999.0,  # Invalid latitude!
                longitude=85.0,
            ),
        ],
    )
    rep = DataValidator.validate_track_series(series)
    assert rep.status == ValidationSeverity.ERROR
    assert rep.is_valid is False
    assert any("coordinate_bounds" in c.check_name for c in rep.checks if not c.passed)


def test_validate_track_series_non_monotonic():
    series = CycloneTrackSeries(
        storm_id="TEST03",
        storm_name="TIME_WARP",
        season=2023,
        basin="NI",
        points=[
            CycloneTrackPoint(
                storm_id="TEST03",
                storm_name="TIME_WARP",
                season=2023,
                basin="NI",
                timestamp_utc="2023-05-10T12:00:00Z",
                latitude=12.0,
                longitude=85.0,
            ),
            CycloneTrackPoint(
                storm_id="TEST03",
                storm_name="TIME_WARP",
                season=2023,
                basin="NI",
                timestamp_utc="2023-05-10T06:00:00Z",  # Earlier timestamp!
                latitude=12.5,
                longitude=85.2,
            ),
        ],
    )
    rep = DataValidator.validate_track_series(series)
    assert rep.status == ValidationSeverity.ERROR
    assert any("chronological_order" in c.check_name for c in rep.checks if not c.passed)


def test_validate_satellite_grid():
    grid = np.full((64, 64), 280.0, dtype=np.float32)
    grid[20:30, 20:30] = 200.0  # Cold convective core

    rep = DataValidator.validate_satellite_grid(grid, channel_name="IRWIN")
    assert rep.status == ValidationSeverity.VALID

    # Grid with inf
    bad_grid = grid.copy()
    bad_grid[0, 0] = np.inf
    rep_bad = DataValidator.validate_satellite_grid(bad_grid, channel_name="IRWIN")
    assert rep_bad.status == ValidationSeverity.ERROR
