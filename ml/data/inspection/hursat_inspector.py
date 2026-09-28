"""
HURSAT Dataset Inspection Utility.
Inspects NetCDF HURSAT files and extracts dimensions, variables, coordinates, units,
spatial range, and missing-value statistics without altering raw files.
"""

import os
from typing import Any, Dict, List, Optional
import numpy as np

from ml.data.io.netcdf3 import NetCDF3Dataset


class HursatInspectionReport:
    """Structured inspection summary for a HURSAT NetCDF file."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_size_bytes = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        self.global_attributes: Dict[str, Any] = {}
        self.dimensions: Dict[str, int] = {}
        self.variables: Dict[str, Dict[str, Any]] = {}
        self.spatial_bounds: Optional[Dict[str, float]] = None
        self.time_info: Optional[str] = None
        self.storm_id: Optional[str] = None
        self.storm_name: Optional[str] = None
        self.missing_value_stats: Dict[str, Dict[str, Any]] = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "file_size_bytes": self.file_size_bytes,
            "storm_id": self.storm_id,
            "storm_name": self.storm_name,
            "time_info": self.time_info,
            "dimensions": self.dimensions,
            "spatial_bounds": self.spatial_bounds,
            "variables": self.variables,
            "missing_value_stats": self.missing_value_stats,
            "global_attributes": self.global_attributes,
        }

    def print_summary(self):
        print(f"=== HURSAT INSPECTION REPORT ===")
        print(f"File: {self.file_path} ({self.file_size_bytes:,} bytes)")
        print(f"Storm Identifier: {self.storm_id or 'Unknown'}")
        print(f"Storm Name:       {self.storm_name or 'Unknown'}")
        print(f"Time/Timestamp:   {self.time_info or 'Unknown'}")
        print(f"\nDimensions:")
        for dname, dlen in self.dimensions.items():
            print(f"  - {dname}: {dlen}")

        if self.spatial_bounds:
            print(f"\nSpatial Range:")
            print(f"  Latitude:  {self.spatial_bounds.get('lat_min', 'N/A')} to {self.spatial_bounds.get('lat_max', 'N/A')} deg N")
            print(f"  Longitude: {self.spatial_bounds.get('lon_min', 'N/A')} to {self.spatial_bounds.get('lon_max', 'N/A')} deg E")

        print(f"\nVariables ({len(self.variables)}):")
        for vname, vinfo in self.variables.items():
            units = vinfo.get("units", "None")
            dtype = vinfo.get("dtype", "Unknown")
            shape = vinfo.get("shape", ())
            dims = vinfo.get("dimensions", ())
            print(f"  - {vname}{dims} [{dtype}, units='{units}']")
            if vname in self.missing_value_stats:
                st = self.missing_value_stats[vname]
                print(f"      Valid: {st['valid_count']} | NaN/Fill: {st['nan_count']} ({st['missing_fraction']:.1%}) | Min: {st.get('min')} | Max: {st.get('max')} | Mean: {st.get('mean')}")


def inspect_hursat_file(file_path: str) -> HursatInspectionReport:
    """Inspects a NetCDF HURSAT file without modifying it."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File does not exist: {file_path}")

    report = HursatInspectionReport(file_path)
    ds = NetCDF3Dataset(file_path, mode="r")

    report.global_attributes = dict(ds.attributes)
    report.dimensions = dict(ds.dimensions)
    report.storm_id = ds.attributes.get("storm_id") or ds.attributes.get("SID") or ds.attributes.get("id")
    report.storm_name = ds.attributes.get("storm_name") or ds.attributes.get("NAME") or ds.attributes.get("storm")
    report.time_info = ds.attributes.get("time_coverage_start") or ds.attributes.get("time") or ds.attributes.get("date")

    # Spatial coordinates
    lat_arr = None
    lon_arr = None
    if "lat" in ds.variables:
        lat_arr = ds.variables["lat"].data
    elif "latitude" in ds.variables:
        lat_arr = ds.variables["latitude"].data

    if "lon" in ds.variables:
        lon_arr = ds.variables["lon"].data
    elif "longitude" in ds.variables:
        lon_arr = ds.variables["longitude"].data

    if lat_arr is not None and lon_arr is not None:
        report.spatial_bounds = {
            "lat_min": float(np.nanmin(lat_arr)),
            "lat_max": float(np.nanmax(lat_arr)),
            "lon_min": float(np.nanmin(lon_arr)),
            "lon_max": float(np.nanmax(lon_arr)),
        }

    for vname, var in ds.variables.items():
        atts = dict(var.attributes)
        vinfo = {
            "name": vname,
            "dimensions": var.dimensions,
            "shape": list(var.shape),
            "dtype": str(var.dtype),
            "units": atts.get("units"),
            "long_name": atts.get("long_name"),
            "attributes": atts,
        }
        report.variables[vname] = vinfo

        # Missing value and numeric statistics
        arr = var.data
        if np.issubdtype(arr.dtype, np.number):
            nan_count = int(np.isnan(arr).sum())
            total = int(arr.size)
            valid_arr = arr[~np.isnan(arr)]
            valid_count = int(valid_arr.size)
            missing_frac = (nan_count / total) if total > 0 else 0.0

            stats = {
                "total_elements": total,
                "nan_count": nan_count,
                "valid_count": valid_count,
                "missing_fraction": missing_frac,
            }
            if valid_count > 0:
                stats["min"] = round(float(np.min(valid_arr)), 2)
                stats["max"] = round(float(np.max(valid_arr)), 2)
                stats["mean"] = round(float(np.mean(valid_arr)), 2)
                stats["std"] = round(float(np.std(valid_arr)), 2)
            report.missing_value_stats[vname] = stats

    return report
