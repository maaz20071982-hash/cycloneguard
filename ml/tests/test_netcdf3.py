"""
Unit tests for zero-dependency NetCDF-3 Classic / 64-bit Offset IO engine.
"""

import os
import tempfile
# pyrefly: ignore [missing-import]
import numpy as np
import pytest

from ml.data.io.netcdf3 import NetCDF3Dataset, NC_FLOAT, NC_SHORT, NC_INT, NC_CHAR


def test_netcdf3_roundtrip():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.nc")

        ds = NetCDF3Dataset()
        ds.attributes["title"] = "CycloneGuard NetCDF-3 Test"
        ds.attributes["institution"] = "CycloneGuard Research Team"
        ds.attributes["history"] = "Created for unit testing"
        ds.attributes["numeric_attr"] = 42

        ds.create_dimension("time", 2)
        ds.create_dimension("lat", 4)
        ds.create_dimension("lon", 4)

        lats = np.array([10.0, 11.0, 12.0, 13.0], dtype=np.float32)
        lons = np.array([80.0, 81.0, 82.0, 83.0], dtype=np.float32)
        data = np.arange(32, dtype=np.float32).reshape((2, 4, 4))

        ds.create_variable("lat", NC_FLOAT, ("lat",), {"units": "degrees_north"}, lats)
        ds.create_variable("lon", NC_FLOAT, ("lon",), {"units": "degrees_east"}, lons)
        ds.create_variable(
            "IRWIN",
            NC_FLOAT,
            ("time", "lat", "lon"),
            {"units": "Kelvin", "long_name": "Infrared Window Brightness Temperature"},
            data,
        )

        ds.write(test_file)
        assert os.path.exists(test_file)
        assert os.path.getsize(test_file) > 0

        # Read back
        ds_read = NetCDF3Dataset(test_file, mode="r")
        assert ds_read.dimensions["lat"] == 4
        assert ds_read.dimensions["lon"] == 4
        assert ds_read.dimensions["time"] == 2
        assert ds_read.attributes["title"] == "CycloneGuard NetCDF-3 Test"
        assert ds_read.attributes["numeric_attr"] == 42

        assert "IRWIN" in ds_read.variables
        ir_var = ds_read.variables["IRWIN"]
        assert ir_var.shape == (2, 4, 4)
        assert ir_var.attributes["units"] == "Kelvin"
        np.testing.assert_array_almost_equal(ir_var.data, data)


def test_netcdf3_scale_factor_and_fill_value():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "scaled.nc")

        ds = NetCDF3Dataset()
        ds.create_dimension("x", 3)

        raw_ints = np.array([100, 200, -999], dtype=np.int16)
        ds.create_variable(
            "temperature",
            NC_SHORT,
            ("x",),
            {"scale_factor": 0.1, "add_offset": 200.0, "_FillValue": -999},
            raw_ints,
        )
        ds.write(test_file)

        ds_read = NetCDF3Dataset(test_file, mode="r")
        arr = ds_read.variables["temperature"].data
        # 100 * 0.1 + 200 = 210.0
        # 200 * 0.1 + 200 = 220.0
        # -999 was _FillValue -> np.nan
        assert abs(arr[0] - 210.0) < 1e-4
        assert abs(arr[1] - 220.0) < 1e-4
        assert np.isnan(arr[2])
