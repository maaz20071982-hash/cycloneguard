"""
Unit tests for data normalization engine.
"""

from datetime import datetime, timezone
import numpy as np
import pytest

from ml.data.normalization.normalizer import DataNormalizer


def test_timestamp_normalization():
    iso, epoch = DataNormalizer.normalize_timestamp_to_utc("2023-05-12 06:00:00")
    assert iso == "2023-05-12T06:00:00Z"
    assert epoch > 0

    iso2, _ = DataNormalizer.normalize_timestamp_to_utc("2023-05-12T06:00:00Z")
    assert iso2 == "2023-05-12T06:00:00Z"


def test_longitude_normalization():
    # Longitude within [-180, 180]
    assert DataNormalizer.normalize_longitude(88.5) == 88.5
    assert DataNormalizer.normalize_longitude(-88.5) == -88.5
    # Longitude in [0, 360] -> [-180, 180]
    assert DataNormalizer.normalize_longitude(270.0) == -90.0
    assert DataNormalizer.normalize_longitude(350.0) == -10.0


def test_latitude_normalization():
    assert DataNormalizer.normalize_latitude(15.5) == 15.5
    with pytest.raises(ValueError):
        DataNormalizer.normalize_latitude(105.0)


def test_orient_spatial_grid():
    arr = np.array([[1, 2], [3, 4]], dtype=np.float32)
    desc_lats = np.array([20.0, 10.0])  # Descending North to South
    asc_lons = np.array([80.0, 90.0])

    oriented_arr, out_lats, out_lons = DataNormalizer.orient_spatial_grid(arr, desc_lats, asc_lons)
    assert out_lats[0] < out_lats[-1]  # Should be ascending now
    # Flipped along axis 0
    assert oriented_arr[0, 0] == 3
    assert oriented_arr[1, 0] == 1


def test_standardize_missing_values():
    arr = np.array([10.0, -999.0, 20.0, -32768.0], dtype=np.float32)
    norm_arr = DataNormalizer.standardize_missing_values(arr, [-999.0, -32768.0])
    assert norm_arr[0] == 10.0
    assert np.isnan(norm_arr[1])
    assert norm_arr[2] == 20.0
    assert np.isnan(norm_arr[3])
