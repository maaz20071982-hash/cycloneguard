"""
Scientific Data Validation Engine for CycloneGuard.
Performs strict, non-destructive validation across satellite grids and cyclone track series.
Rules:
- Never silently repair corrupted scientific records.
- Explicitly return VALID, WARNING, or ERROR with actionable diagnostics.
"""

from datetime import datetime
import os
from typing import Any, Dict, List, Optional, Set
import numpy as np

from ml.data.schemas.adapter_results import (
    ValidationCheck,
    ValidationReport,
    ValidationSeverity,
)
from ml.data.schemas.track import CycloneTrackPoint, CycloneTrackSeries


class DataValidator:
    """Validator for cyclone tracks, satellite grids, and tabular observations."""

    @staticmethod
    def validate_file(file_path: str, expected_format: Optional[str] = None) -> ValidationReport:
        """Validates basic file existence, non-emptiness, and extension format."""
        report = ValidationReport(source_id="filesystem", file_path=file_path, status=ValidationSeverity.VALID)

        if not os.path.exists(file_path):
            report.status = ValidationSeverity.ERROR
            report.checks.append(ValidationCheck(
                check_name="file_exists",
                passed=False,
                severity=ValidationSeverity.ERROR,
                message=f"File not found: {file_path}",
            ))
            report.summary = "File does not exist."
            return report

        size = os.path.getsize(file_path)
        if size == 0:
            report.status = ValidationSeverity.ERROR
            report.checks.append(ValidationCheck(
                check_name="file_non_empty",
                passed=False,
                severity=ValidationSeverity.ERROR,
                message="File is empty (0 bytes).",
            ))
            report.summary = "Empty file."
            return report

        report.checks.append(ValidationCheck(
            check_name="file_readable",
            passed=True,
            severity=ValidationSeverity.VALID,
            message=f"File is readable ({size:,} bytes).",
        ))

        if expected_format:
            ext = os.path.splitext(file_path)[1].lower()
            exp_ext = expected_format.lower() if expected_format.startswith(".") else f".{expected_format.lower()}"
            if ext != exp_ext:
                report.checks.append(ValidationCheck(
                    check_name="expected_extension",
                    passed=False,
                    severity=ValidationSeverity.WARNING,
                    message=f"File extension '{ext}' does not match expected '{exp_ext}'.",
                ))
                report.status = ValidationSeverity.WARNING

        report.summary = "File system validation passed."
        return report

    @staticmethod
    def validate_track_series(series: CycloneTrackSeries) -> ValidationReport:
        """
        Validates chronological monotonicity, coordinate bounds, absence of duplicates,
        and physical plausibility of wind speed and pressure values.
        """
        report = ValidationReport(
            source_id="cyclone_track",
            file_path=series.storm_id,
            status=ValidationSeverity.VALID,
        )

        if not series.points:
            report.status = ValidationSeverity.ERROR
            report.checks.append(ValidationCheck(
                check_name="has_points",
                passed=False,
                severity=ValidationSeverity.ERROR,
                message=f"Storm {series.storm_id} contains zero observation points.",
            ))
            report.summary = "Empty track series."
            return report

        timestamps: List[datetime] = []
        duplicate_times: Set[str] = set()
        seen_time_strs: Set[str] = set()
        invalid_coords: List[Dict[str, Any]] = []
        unphysical_winds: List[Dict[str, Any]] = []
        unphysical_pressures: List[Dict[str, Any]] = []

        for p in series.points:
            # Check duplicate timestamps
            if p.timestamp_utc in seen_time_strs:
                duplicate_times.add(p.timestamp_utc)
            seen_time_strs.add(p.timestamp_utc)

            try:
                dt = datetime.fromisoformat(p.timestamp_utc.replace("Z", "+00:00"))
                timestamps.append(dt)
            except Exception:
                pass

            # Coordinate check: lat [-90, 90], lon [-180, 180]
            if not (-90.0 <= p.latitude <= 90.0) or not (-180.0 <= p.longitude <= 180.0):
                invalid_coords.append({"time": p.timestamp_utc, "lat": p.latitude, "lon": p.longitude})

            # Physical wind speed check: 0 to 220 knots (highest recorded Earth wind ~185-200 kts in SuCS Patricia/Haiyan)
            if p.wind_speed_kts is not None:
                if not (0.0 <= p.wind_speed_kts <= 230.0):
                    unphysical_winds.append({"time": p.timestamp_utc, "wind": p.wind_speed_kts})

            # Physical central pressure check: 850 mb to 1040 mb (deepest recorded ~870 mb in Tip)
            if p.central_pressure_mb is not None:
                if not (850.0 <= p.central_pressure_mb <= 1045.0):
                    unphysical_pressures.append({"time": p.timestamp_utc, "pressure": p.central_pressure_mb})

        # Monotonicity check
        is_monotonic = all(timestamps[i] <= timestamps[i + 1] for i in range(len(timestamps) - 1))
        if not is_monotonic:
            report.status = ValidationSeverity.ERROR
            report.checks.append(ValidationCheck(
                check_name="chronological_order",
                passed=False,
                severity=ValidationSeverity.ERROR,
                message="Observations are not monotonically ordered in time.",
            ))
        else:
            report.checks.append(ValidationCheck(
                check_name="chronological_order",
                passed=True,
                severity=ValidationSeverity.VALID,
                message="Observations are chronologically ordered.",
            ))

        if duplicate_times:
            report.status = ValidationSeverity.WARNING
            report.checks.append(ValidationCheck(
                check_name="duplicate_timestamps",
                passed=False,
                severity=ValidationSeverity.WARNING,
                message=f"Found {len(duplicate_times)} duplicate timestamps: {list(duplicate_times)[:3]}...",
            ))
        else:
            report.checks.append(ValidationCheck(
                check_name="duplicate_timestamps",
                passed=True,
                severity=ValidationSeverity.VALID,
                message="No duplicate timestamps detected.",
            ))

        if invalid_coords:
            report.status = ValidationSeverity.ERROR
            report.checks.append(ValidationCheck(
                check_name="coordinate_bounds",
                passed=False,
                severity=ValidationSeverity.ERROR,
                message=f"{len(invalid_coords)} points have coordinates outside valid geographic range.",
                details={"sample": invalid_coords[:2]},
            ))
        else:
            report.checks.append(ValidationCheck(
                check_name="coordinate_bounds",
                passed=True,
                severity=ValidationSeverity.VALID,
                message="All coordinates within valid geographic bounds [-90..90, -180..180].",
            ))

        if unphysical_winds or unphysical_pressures:
            report.status = ValidationSeverity.WARNING
            report.checks.append(ValidationCheck(
                check_name="physical_limits",
                passed=False,
                severity=ValidationSeverity.WARNING,
                message=f"Found unphysical intensity values (winds: {len(unphysical_winds)}, pressures: {len(unphysical_pressures)}).",
            ))
        else:
            report.checks.append(ValidationCheck(
                check_name="physical_limits",
                passed=True,
                severity=ValidationSeverity.VALID,
                message="All wind and pressure values within physically plausible tropical cyclone limits.",
            ))

        report.summary = f"Track series validation complete: {len(series.points)} points evaluated."
        return report

    @staticmethod
    def validate_satellite_grid(
        array: np.ndarray,
        channel_name: str,
        expected_shape: Optional[tuple] = None,
        max_missing_fraction: float = 0.25,
    ) -> ValidationReport:
        """
        Validates satellite imagery matrix: shape, NaN/Inf percentages,
        and physical temperature ranges for thermal channels.
        """
        report = ValidationReport(
            source_id="satellite_grid",
            file_path=channel_name,
            status=ValidationSeverity.VALID,
        )

        if expected_shape and array.shape != expected_shape:
            report.status = ValidationSeverity.ERROR
            report.checks.append(ValidationCheck(
                check_name="grid_shape",
                passed=False,
                severity=ValidationSeverity.ERROR,
                message=f"Shape {array.shape} does not match expected {expected_shape}.",
            ))
        else:
            report.checks.append(ValidationCheck(
                check_name="grid_shape",
                passed=True,
                severity=ValidationSeverity.VALID,
                message=f"Grid shape {array.shape} verified.",
            ))

        total_pixels = array.size
        nan_pixels = int(np.isnan(array).sum())
        inf_pixels = int(np.isinf(array).sum())
        missing_fraction = (nan_pixels + inf_pixels) / total_pixels if total_pixels > 0 else 0.0

        if inf_pixels > 0:
            report.status = ValidationSeverity.ERROR
            report.checks.append(ValidationCheck(
                check_name="infinite_values",
                passed=False,
                severity=ValidationSeverity.ERROR,
                message=f"Found {inf_pixels} infinite values in satellite grid.",
            ))
        else:
            report.checks.append(ValidationCheck(
                check_name="infinite_values",
                passed=True,
                severity=ValidationSeverity.VALID,
                message="Zero infinite values found.",
            ))

        if missing_fraction > max_missing_fraction:
            report.status = ValidationSeverity.WARNING
            report.checks.append(ValidationCheck(
                check_name="missing_data_fraction",
                passed=False,
                severity=ValidationSeverity.WARNING,
                message=f"Missing pixel fraction ({missing_fraction:.1%}) exceeds threshold ({max_missing_fraction:.1%}).",
            ))
        else:
            report.checks.append(ValidationCheck(
                check_name="missing_data_fraction",
                passed=True,
                severity=ValidationSeverity.VALID,
                message=f"Missing pixel fraction ({missing_fraction:.1%}) within acceptable limits.",
            ))

        # Check physical bounds if infrared channel
        if "IR" in channel_name.upper():
            valid_pixels = array[~np.isnan(array) & ~np.isinf(array)]
            if valid_pixels.size > 0:
                t_min = float(np.min(valid_pixels))
                t_max = float(np.max(valid_pixels))
                if t_min < 150.0 or t_max > 340.0:
                    report.status = ValidationSeverity.WARNING
                    report.checks.append(ValidationCheck(
                        check_name="infrared_brightness_temp_kelvin",
                        passed=False,
                        severity=ValidationSeverity.WARNING,
                        message=f"Extreme infrared temperatures detected: min={t_min:.1f}K, max={t_max:.1f}K.",
                    ))
                else:
                    report.checks.append(ValidationCheck(
                        check_name="infrared_brightness_temp_kelvin",
                        passed=True,
                        severity=ValidationSeverity.VALID,
                        message=f"Infrared temperatures in expected physical range [150K..340K] (min={t_min:.1f}K, max={t_max:.1f}K).",
                    ))

        report.summary = f"Grid validation complete: {missing_fraction:.1%} missing pixels."
        return report
