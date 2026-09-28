"""
Phase 5: Historical HURSAT Validation Engine.
Systematically audits all downloaded NetCDF files in data/raw/hursat/:
- file integrity
- dimensions (lat, lon)
- timestamps (time_coverage_start)
- coordinates (WGS-84 degree bounds)
- variables/channels (IRWIN, IRWVP, VSCHN)
- units & fill values
- geographic extent
- missing data fractions
- duplicate asset identity detection
Outputs data/reports/hursat_validation_report.json and aggregate statistics.
"""

from collections import defaultdict
from datetime import datetime
import json
import os
from typing import Dict, List, Any, Optional

from ml.data.validation.source_validators.hursat_validator import HURSATSourceValidator, SourceValidationResult
from ml.data.acquisition.config import default_config


def run_historical_hursat_validation(
    raw_hursat_dir: Optional[str] = None,
    output_report_path: str = "data/reports/hursat_validation_report.json",
) -> Dict[str, Any]:
    base_dir = raw_hursat_dir or os.path.join(default_config.raw_data_dir, "hursat")
    validator = HURSATSourceValidator()

    # Discover all .nc files
    all_nc_files = []
    for root, _, files in os.walk(base_dir):
        for f in files:
            if f.endswith(".nc"):
                all_nc_files.append(os.path.join(root, f))

    all_nc_files.sort()

    report = {
        "report_version": "1.0.0",
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "total_files_audited": len(all_nc_files),
        "valid_files_count": 0,
        "invalid_files_count": 0,
        "duplicate_assets_count": 0,
        "storms_audited": 0,
        "storms": {},
        "channel_availability": defaultdict(int),
        "aggregate_ranges": {},
        "invalid_files": [],
    }

    seen_asset_ids = set()
    storm_stats = defaultdict(lambda: {"total": 0, "valid": 0, "invalid": 0, "nc_files": []})
    all_irwin_ranges = []
    all_irwvp_ranges = []

    for fpath in all_nc_files:
        fname = os.path.basename(fpath)
        # Identify storm ID from directory or filename
        parent_dir = os.path.basename(os.path.dirname(fpath))
        sid = parent_dir if parent_dir.startswith("20") else fname.split(".")[0]

        # Duplicate asset detection
        if fname in seen_asset_ids:
            report["duplicate_assets_count"] += 1
        seen_asset_ids.add(fname)

        val_res: SourceValidationResult = validator.validate_hursat_file(fpath)

        storm_stats[sid]["total"] += 1
        if val_res.is_valid:
            report["valid_files_count"] += 1
            storm_stats[sid]["valid"] += 1
        else:
            report["invalid_files_count"] += 1
            storm_stats[sid]["invalid"] += 1
            report["invalid_files"].append({
                "file_path": fpath,
                "reasons": [c.message for c in val_res.checks if not c.passed],
            })

        for v in val_res.variables:
            report["channel_availability"][v] += 1

        if "IRWIN" in val_res.physical_ranges:
            all_irwin_ranges.append(val_res.physical_ranges["IRWIN"])
        if "IRWVP" in val_res.physical_ranges:
            all_irwvp_ranges.append(val_res.physical_ranges["IRWVP"])

        storm_stats[sid]["nc_files"].append({
            "file_name": fname,
            "is_valid": val_res.is_valid,
            "time_metadata": val_res.time_metadata,
            "dimensions": val_res.dimensions,
            "geographic_extent": val_res.geographic_extent,
            "missing_data_fraction": val_res.missing_data_fraction,
            "irwin_range": val_res.physical_ranges.get("IRWIN"),
        })

    report["storms_audited"] = len(storm_stats)
    report["storms"] = dict(storm_stats)
    report["channel_availability"] = dict(report["channel_availability"])

    # Aggregate physical ranges
    if all_irwin_ranges:
        report["aggregate_ranges"]["IRWIN"] = {
            "min_observed_kelvin": min(r["min"] for r in all_irwin_ranges),
            "max_observed_kelvin": max(r["max"] for r in all_irwin_ranges),
            "mean_observed_kelvin": round(sum(r["mean"] for r in all_irwin_ranges) / len(all_irwin_ranges), 2),
        }
    if all_irwvp_ranges:
        report["aggregate_ranges"]["IRWVP"] = {
            "min_observed_kelvin": min(r["min"] for r in all_irwvp_ranges),
            "max_observed_kelvin": max(r["max"] for r in all_irwvp_ranges),
            "mean_observed_kelvin": round(sum(r["mean"] for r in all_irwvp_ranges) / len(all_irwvp_ranges), 2),
        }

    os.makedirs(os.path.dirname(os.path.abspath(output_report_path)), exist_ok=True)
    with open(output_report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return report


if __name__ == "__main__":
    from typing import Optional
    rep = run_historical_hursat_validation()
    print("=== HURSAT Validation Summary ===")
    print(f"Total files audited: {rep['total_files_audited']}")
    print(f"Valid files: {rep['valid_files_count']}")
    print(f"Invalid files: {rep['invalid_files_count']}")
    print(f"Duplicate assets: {rep['duplicate_assets_count']}")
    print(f"Storms audited: {rep['storms_audited']}")
    print(f"IRWIN range: {rep['aggregate_ranges'].get('IRWIN')}")
    print(f"IRWVP range: {rep['aggregate_ranges'].get('IRWVP')}")
    for sid, sinfo in rep["storms"].items():
        print(f" - {sid}: {sinfo['valid']}/{sinfo['total']} valid NetCDF files")
