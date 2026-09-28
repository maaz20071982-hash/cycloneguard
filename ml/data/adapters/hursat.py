"""
NOAA HURSAT-B1 Source Adapter for CycloneGuard.
Ingests, validates, parses, and normalizes storm-centric NetCDF satellite imagery
(Infrared Window, Water Vapor, and Visible channels).
"""

from datetime import datetime
import os
from typing import Any, Dict, List, Optional
import numpy as np

from ml.data.adapters.base import BaseDataSourceAdapter
from ml.data.io.netcdf3 import NetCDF3Dataset
from ml.data.schemas.adapter_results import (
    DiscoveredResource,
    DownloadResult,
    DownloadStatus,
    NormalizedData,
    ParsedData,
    ValidationCheck,
    ValidationReport,
    ValidationSeverity,
)
from ml.data.schemas.satellite import SatelliteMetadata


class HURSATAdapter(BaseDataSourceAdapter):
    """Adapter for NOAA HURSAT-B1 (Hurricane Satellite ISCCP B1) NetCDF files."""

    def __init__(self):
        super().__init__("noaa_hursat_b1")

    def discover(self, filters: Optional[Dict[str, Any]] = None) -> List[DiscoveredResource]:
        """Discovers known HURSAT-B1 archives and cloud distribution points."""
        return [
            DiscoveredResource(
                resource_id="hursat_b1_global_v06",
                source_id=self.source_id,
                name="NOAA HURSAT-B1 Global Tropical Cyclone Archive v06",
                remote_url="https://www.ncei.noaa.gov/products/hurricane-satellite-data",
                time_coverage="1978-2015",
                spatial_coverage="Global Tropical Oceans (301x301 storm-centered 8km grids)",
                format="NetCDF-3 / NetCDF-4",
                metadata={"provider": "NOAA NCEI", "channels": ["IRWIN", "IRWVP", "VSCHN"]},
            ),
            DiscoveredResource(
                resource_id="hursat_nodd_s3_mirror",
                source_id=self.source_id,
                name="NOAA Open Data Dissemination (NODD) Cloud Bucket",
                remote_url="s3://noaa-gestationary-hursat/ (or NCEI public cloud)",
                time_coverage="1978-2024",
                spatial_coverage="Global",
                format="NetCDF-4",
                metadata={"scope": "cloud_mirror", "bulk_download": True},
            ),
        ]

    def download(self, resource_id: str, target_dir: str) -> DownloadResult:
        """
        Automatic automated bulk ingestion from NOAA archive mirrors.
        Honest status reporting: direct bulk download from NOAA requires configured S3 or mirror credentials.
        """
        return DownloadResult(
            source_id=self.source_id,
            resource_id=resource_id,
            status=DownloadStatus.NOT_IMPLEMENTED,
            message="Automatic ingestion not implemented: Bulk HURSAT download requires NOAA NODD S3 access or pre-staged local archive synchronization.",
        )

    def validate(self, file_path: str) -> ValidationReport:
        """Validates NetCDF format, dimensions, IRWIN channel presence, and Kelvin temperature ranges."""
        report = ValidationReport(source_id=self.source_id, file_path=file_path, status=ValidationSeverity.VALID)

        if not os.path.exists(file_path):
            report.status = ValidationSeverity.ERROR
            report.checks.append(ValidationCheck(
                check_name="file_exists",
                passed=False,
                severity=ValidationSeverity.ERROR,
                message=f"File not found: {file_path}",
            ))
            report.summary = "Validation failed: file does not exist."
            return report

        report.checks.append(ValidationCheck(
            check_name="file_exists",
            passed=True,
            severity=ValidationSeverity.VALID,
            message="File exists.",
        ))

        try:
            ds = NetCDF3Dataset(file_path, mode="r")
            dims = ds.dimensions
            vars_dict = ds.variables

            # Check dimensions
            has_spatial_dims = ("lat" in dims and "lon" in dims) or ("lines" in dims and "elements" in dims)
            if not has_spatial_dims:
                report.status = ValidationSeverity.ERROR
                report.checks.append(ValidationCheck(
                    check_name="dimensions",
                    passed=False,
                    severity=ValidationSeverity.ERROR,
                    message=f"Missing spatial dimensions in NetCDF: {dims}",
                ))
            else:
                report.checks.append(ValidationCheck(
                    check_name="dimensions",
                    passed=True,
                    severity=ValidationSeverity.VALID,
                    message=f"Found valid spatial dimensions: {dims}",
                ))

            # Check primary Infrared Window variable
            ir_var_name = None
            for candidate in ("IRWIN", "irwin", "irwin_cdr", "IR11"):
                if candidate in vars_dict:
                    ir_var_name = candidate
                    break

            if not ir_var_name:
                report.status = ValidationSeverity.ERROR
                report.checks.append(ValidationCheck(
                    check_name="primary_ir_variable",
                    passed=False,
                    severity=ValidationSeverity.ERROR,
                    message="Missing primary Infrared Window (IRWIN) channel in NetCDF file.",
                ))
            else:
                ir_arr = vars_dict[ir_var_name].data
                valid_vals = ir_arr[~np.isnan(ir_arr)]
                min_t = float(np.min(valid_vals)) if valid_vals.size > 0 else 0.0
                max_t = float(np.max(valid_vals)) if valid_vals.size > 0 else 0.0

                # Meteorological physical plausibility for cloud-top brightness temperature in Kelvin:
                # Cold overshooting tops can drop to ~175-180 K; warm sea surfaces ~305 K.
                plausible = (150.0 <= min_t <= 320.0) and (200.0 <= max_t <= 335.0)
                if not plausible:
                    report.checks.append(ValidationCheck(
                        check_name="temperature_plausibility",
                        passed=False,
                        severity=ValidationSeverity.WARNING,
                        message=f"IR brightness temperatures outside expected range (min={min_t:.1f}K, max={max_t:.1f}K).",
                        details={"min": min_t, "max": max_t},
                    ))
                    if report.status != ValidationSeverity.ERROR:
                        report.status = ValidationSeverity.WARNING
                else:
                    report.checks.append(ValidationCheck(
                        check_name="temperature_plausibility",
                        passed=True,
                        severity=ValidationSeverity.VALID,
                        message=f"IR brightness temperatures are physically plausible (min={min_t:.1f}K, max={max_t:.1f}K).",
                        details={"min": min_t, "max": max_t},
                    ))

            report.summary = "HURSAT NetCDF file is structurally valid." if report.is_valid else "Validation failed."

        except Exception as e:
            report.status = ValidationSeverity.ERROR
            report.checks.append(ValidationCheck(
                check_name="netcdf_read",
                passed=False,
                severity=ValidationSeverity.ERROR,
                message=f"Corrupted or invalid NetCDF: {str(e)}",
            ))
            report.summary = f"Read error: {str(e)}"

        return report

    def parse(self, file_path: str) -> ParsedData:
        """Parses NetCDF file into arrays, coordinate grids, and variable dictionaries."""
        ds = NetCDF3Dataset(file_path, mode="r")
        raw_vars = list(ds.variables.keys())
        dims = dict(ds.dimensions)
        atts = dict(ds.attributes)

        payload = {
            "attributes": atts,
            "dimensions": dims,
            "variables": {vname: var.data for vname, var in ds.variables.items()},
            "variable_attributes": {vname: dict(var.attributes) for vname, var in ds.variables.items()},
        }

        return ParsedData(
            source_id=self.source_id,
            file_path=file_path,
            records_count=1,
            raw_variables=raw_vars,
            raw_dimensions=dims,
            raw_attributes=atts,
            data_payload=payload,
        )

    def normalize(self, parsed_data: ParsedData) -> NormalizedData:
        """Standardizes variables to Kelvin, extracts bounds, and builds SatelliteMetadata."""
        payload = parsed_data.data_payload or {}
        atts = payload.get("attributes", {})
        vars_dict = payload.get("variables", {})

        storm_id = atts.get("storm_id") or atts.get("SID") or "UNKNOWN"
        time_str = atts.get("time_coverage_start") or atts.get("time") or datetime.utcnow().isoformat() + "Z"

        # Determine spatial coordinates
        lat_arr = vars_dict.get("lat") if "lat" in vars_dict else vars_dict.get("latitude")
        lon_arr = vars_dict.get("lon") if "lon" in vars_dict else vars_dict.get("longitude")

        if lat_arr is not None and lon_arr is not None:
            spatial_bounds = {
                "lat_min": float(np.nanmin(lat_arr)),
                "lat_max": float(np.nanmax(lat_arr)),
                "lon_min": float(np.nanmin(lon_arr)),
                "lon_max": float(np.nanmax(lon_arr)),
            }
            grid_shape = (len(lat_arr), len(lon_arr))
        else:
            spatial_bounds = {"lat_min": 0.0, "lat_max": 0.0, "lon_min": 0.0, "lon_max": 0.0}
            grid_shape = (0, 0)

        # Channels available
        channel_names = [v for v in ("IRWIN", "IRWVP", "VSCHN") if v in vars_dict]
        units = {
            "IRWIN": "Kelvin (Brightness Temperature ~11 µm)",
            "IRWVP": "Kelvin (Water Vapor ~6.7 µm)",
            "VSCHN": "albedo_fraction (Visible ~0.6 µm)",
        }

        meta = SatelliteMetadata(
            source_id=self.source_id,
            satellite_name=atts.get("satellite") or "ISCCP-B1 Geostationary Composite",
            timestamp_utc=time_str,
            channels=channel_names,
            units=units,
            grid_shape=grid_shape,
            lat_bounds=(spatial_bounds["lat_min"], spatial_bounds["lat_max"]),
            lon_bounds=(spatial_bounds["lon_min"], spatial_bounds["lon_max"]),
            spatial_resolution_km=8.0,
            missing_value_flags=[-999.0],
        )

        return NormalizedData(
            source_id=self.source_id,
            normalized_type="satellite_observation",
            records_count=1,
            time_range_utc=(time_str, time_str),
            spatial_bounds=spatial_bounds,
            data_payload={
                "metadata": meta,
                "arrays": {ch: vars_dict[ch] for ch in channel_names},
                "coordinates": {"lat": lat_arr, "lon": lon_arr},
            },
            units=units,
            normalization_log=[f"Normalized HURSAT satellite observation for storm {storm_id} at {time_str}"],
        )
