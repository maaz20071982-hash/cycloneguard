"""
CLI Tool: Run Satellite Quality Control Suite and generate report.

Usage:
    python -m ml.data.validation.run_satellite_qc
"""

import json
import os
import sys

from ml.data.validation.satellite_qc import SatelliteQualityController


def main():
    print("=== CYCLONEGUARD SATELLITE QUALITY CONTROL AUDIT ===")
    qc = SatelliteQualityController()
    report = qc.run_full_audit()

    root_dir = qc.root_dir
    rep_dir = os.path.join(root_dir, "data", "reports")
    os.makedirs(rep_dir, exist_ok=True)
    rep_path = os.path.join(rep_dir, "satellite_quality_report.json")

    with open(rep_path, "w", encoding="utf-8") as f:
        json.dump(report.model_dump(), f, indent=2)

    print(f"Total Assets Audited:   {report.total_assets_audited}")
    print(f"  Valid Assets:         {report.valid_assets_count}")
    print(f"  Degraded Assets:      {report.degraded_assets_count}")
    print(f"  Rejected Assets:      {report.rejected_assets_count}")
    print(f"Total Patches Audited:  {report.total_patches_audited}")
    print(f"Duplicate Keys Found:   {report.duplicate_records_found}")

    if report.rejection_summary:
        print("\nRejection Reasons Breakdown:")
        for r, cnt in report.rejection_summary.items():
            print(f"  - {r}: {cnt}")

    print(f"\nAudit Report written to: {rep_path}")


if __name__ == "__main__":
    main()
