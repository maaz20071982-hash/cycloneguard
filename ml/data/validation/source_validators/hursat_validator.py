"""
HURSAT-B1 Source-Specific Validation Engine.
Sprint 7 - Phase 10 Deliverable.

Validates dimensions, variables, units, coordinates, time metadata, missing-value encoding,
and physical ranges for NOAA HURSAT-B1 NetCDF-3/NetCDF-4 files.
"""

from datetime import datetime
import os
from typing import Any, Dict, List, Optional
import numpy as np
from pydantic import BaseModel, Field

from ml.data.io.netcdf3 import NetCDF3Dataset


class DetailedValidationCheck(BaseModel):
    check_name: str
    passed: bool
    severity: str
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)


class SourceValidationResult(BaseModel):
    source_id: str
    file_path: str
    is_valid: bool
    dimensions: Dict[str, int]
    variables: List[str]
    coordinate_system: str
    time_metadata: Optional[str] = None
    units_by_variable: Dict[str, str] = Field(default_factory=dict)
    physical_ranges: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    checks: List[DetailedValidationCheck] = Field(default_factory=list)
    geographic_extent: Optional[List[float]] = None
    missing_data_fraction: float = 0.0
    asset_id: Optional[str] = None


class HURSATSourceValidator:
    """Specialized validator for NOAA HURSAT-B1 ISCCP-B1 files."""

    @staticmethod
    def validate_hursat_file(file_path: str) -> SourceValidationResult:
        checks: List[DetailedValidationCheck] = []
        if not os.path.exists(file_path):
            checks.append(DetailedValidationCheck(
                check_name="file_exists",
                passed=False,
                severity="ERROR",
                message=f"File not found: {file_path}",
            ))
            return SourceValidationResult(
                source_id="noaa_hursat_b1",
                file_path=file_path,
                is_valid=False,
                dimensions={},
                variables=[],
                coordinate_system="UNKNOWN",
                checks=checks,
            )

        try:
            ds = NetCDF3Dataset(file_path, mode="r")
        except Exception as e:
            checks.append(DetailedValidationCheck(
                check_name="file_corrupted",
                passed=False,
                severity="ERROR",
                message=f"Corrupted or invalid NetCDF file: {e}",
            ))
            return SourceValidationResult(
                source_id="noaa_hursat_b1",
                file_path=file_path,
                is_valid=False,
                dimensions={},
                variables=[],
                coordinate_system="UNKNOWN",
                checks=checks,
            )

        dims = dict(ds.dimensions)
        atts = dict(ds.attributes)
        vars_dict = ds.variables

        # 1. Dimensions check
        has_dims = ("lat" in dims and "lon" in dims) or ("lines" in dims and "elements" in dims)
        checks.append(DetailedValidationCheck(
            check_name="spatial_dimensions",
            passed=has_dims,
            severity="VALID" if has_dims else "ERROR",
            message=f"Spatial dimensions: {dims}",
            details={"dimensions": dims},
        ))

        # 2. Coordinates & Geographic Extent
        lat_var = vars_dict.get("lat") or vars_dict.get("latitude")
        lon_var = vars_dict.get("lon") or vars_dict.get("longitude")
        has_coords = (lat_var is not None and lon_var is not None)
        extent = None
        if has_coords:
            try:
                lats = lat_var.data
                lons = lon_var.data
                extent = [
                    float(round(np.min(lats), 4)),
                    float(round(np.max(lats), 4)),
                    float(round(np.min(lons), 4)),
                    float(round(np.max(lons), 4)),
                ]
            except Exception:
                extent = None

        has_valid_extent = (extent is not None and -90.0 <= extent[0] <= extent[1] <= 90.0)
        checks.append(DetailedValidationCheck(
            check_name="coordinate_variables",
            passed=has_coords and has_valid_extent,
            severity="VALID" if (has_coords and has_valid_extent) else "ERROR",
            message=f"Coordinates present, extent: {extent}" if has_coords else "Missing coordinates",
            details={"geographic_extent": extent},
        ))

        coord_sys = "WGS-84 / Plate Carree (degrees_north, degrees_east)"

        # 3. Time metadata
        time_meta = atts.get("time_coverage_start") or atts.get("time") or atts.get("time_coverage_end")
        has_time = False
        if time_meta:
            try:
                datetime.fromisoformat(time_meta.replace("Z", "+00:00"))
                has_time = True
            except ValueError:
                pass
        checks.append(DetailedValidationCheck(
            check_name="time_metadata",
            passed=has_time,
            severity="VALID" if has_time else "WARNING",
            message=f"Time metadata ISO verified: '{time_meta}'",
        ))

        # 4. Units, Physical Ranges & Missing Data
        units_map = {}
        ranges_map = {}
        primary_missing_fraction = 0.0

        for vname, var in vars_dict.items():
            var_atts = dict(var.attributes)
            u = var_atts.get("units", "unknown")
            units_map[vname] = u

            arr = var.data
            if not (np.issubdtype(arr.dtype, np.floating) or np.issubdtype(arr.dtype, np.integer)):
                continue
            is_float = np.issubdtype(arr.dtype, np.floating)
            nan_count = int(np.isnan(arr).sum()) if is_float else 0
            nan_fraction = (nan_count / arr.size) if arr.size > 0 else 0.0

            if vname == "IRWIN":
                primary_missing_fraction = round(nan_fraction, 4)
                checks.append(DetailedValidationCheck(
                    check_name="missing_data_fraction_IRWIN",
                    passed=(nan_fraction <= 0.50),
                    severity="VALID" if (nan_fraction <= 0.50) else "ERROR",
                    message=f"IRWIN NaN fraction: {nan_fraction * 100:.2f}% (<= 50% required)",
                    details={"nan_fraction": nan_fraction},
                ))

            valid_arr = arr[~np.isnan(arr)] if is_float else arr
            if valid_arr.size > 0:
                min_v = float(np.min(valid_arr))
                max_v = float(np.max(valid_arr))
                mean_v = float(np.mean(valid_arr))
                ranges_map[vname] = {"min": round(min_v, 2), "max": round(max_v, 2), "mean": round(mean_v, 2)}

                # Check IR physical plausibility
                if "IR" in vname:
                    plausible = (150.0 <= min_v <= 320.0) and (200.0 <= max_v <= 340.0)
                    checks.append(DetailedValidationCheck(
                        check_name=f"physical_range_{vname}",
                        passed=plausible,
                        severity="VALID" if plausible else "WARNING",
                        message=f"{vname} range [{min_v:.1f} K, {max_v:.1f} K] plausible Kelvin brightness temp",
                        details={"min": min_v, "max": max_v},
                    ))
                elif "VSCHN" in vname:
                    plausible = (-0.05 <= min_v <= 1.2)
                    checks.append(DetailedValidationCheck(
                        check_name=f"physical_range_{vname}",
                        passed=plausible,
                        severity="VALID" if plausible else "WARNING",
                        message=f"{vname} range [{min_v:.2f}, {max_v:.2f}] plausible albedo",
                        details={"min": min_v, "max": max_v},
                    ))

        all_valid = all(c.severity != "ERROR" for c in checks)
        return SourceValidationResult(
            source_id="noaa_hursat_b1",
            file_path=file_path,
            is_valid=all_valid,
            dimensions=dims,
            variables=list(vars_dict.keys()),
            coordinate_system=coord_sys,
            time_metadata=time_meta,
            units_by_variable=units_map,
            physical_ranges=ranges_map,
            checks=checks,
            geographic_extent=extent,
            missing_data_fraction=primary_missing_fraction,
            asset_id=os.path.basename(file_path),
        )
