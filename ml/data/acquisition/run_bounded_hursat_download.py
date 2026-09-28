"""
Phase 3 & Phase 4: Bounded Historical HURSAT Downloader.
Executes bounded acquisition of target historical North Indian Ocean storms
using ResilientDownloader, unpacks NetCDF assets, verifies local caches,
enforces total budget limits, and generates data/reports/hursat_download_report.json.
"""

from datetime import datetime
import json
import os
import tarfile
from typing import Dict, List, Any, Optional

from ml.data.acquisition.downloader import ResilientDownloader, DownloadExecutionResult
from ml.data.acquisition.config import default_config


def execute_bounded_hursat_download(
    inventory_path: str = "data/manifests/hursat_archive_inventory.jsonl",
    output_report_path: str = "data/reports/hursat_download_report.json",
    max_total_bytes: int = 250 * 1024 * 1024,  # 250 MB total download ceiling
    max_file_bytes: int = 60 * 1024 * 1024,   # 60 MB per file limit
    target_storm_ids: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Downloads and extracts target storm tarballs under strict resource bounds."""
    downloader = ResilientDownloader(default_config)

    records = []
    with open(inventory_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    # Filter target records
    if target_storm_ids:
        targets = [r for r in records if r["storm_id"] in target_storm_ids]
    else:
        targets = [r for r in records if r.get("is_target_storm", False)]

    report = {
        "report_version": "1.0.0",
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "limits": {
            "max_total_bytes": max_total_bytes,
            "max_file_bytes": max_file_bytes,
        },
        "discovered": len(targets),
        "attempted": 0,
        "downloaded": 0,
        "already_cached": 0,
        "skipped": 0,
        "failed": 0,
        "corrupted": 0,
        "total_bytes_downloaded": 0,
        "total_netcdf_files_extracted": 0,
        "storm_results": [],
    }

    current_download_bytes = 0

    for rec in targets:
        sid = rec["storm_id"]
        sname = rec["storm_name"]
        fname = rec["file_name"]
        url = rec["remote_location"]
        expected_size = rec.get("expected_size_bytes") or 0

        storm_raw_dir = os.path.join(default_config.raw_data_dir, "hursat", sid)
        os.makedirs(storm_raw_dir, exist_ok=True)
        local_tar_path = os.path.join(storm_raw_dir, fname)

        storm_res = {
            "storm_id": sid,
            "storm_name": sname,
            "file_name": fname,
            "remote_url": url,
            "expected_size_bytes": expected_size,
            "status": "PENDING",
            "extracted_nc_count": 0,
            "error": None,
        }

        # Check total budget limit
        if expected_size and (current_download_bytes + expected_size > max_total_bytes):
            if not (os.path.exists(local_tar_path) and os.path.getsize(local_tar_path) > 0):
                storm_res["status"] = "SKIPPED_BUDGET_EXCEEDED"
                report["skipped"] += 1
                report["storm_results"].append(storm_res)
                continue

        report["attempted"] += 1

        # Download or use cache
        dl_res: DownloadExecutionResult = downloader.download_file(
            url=url,
            target_path=local_tar_path,
            max_bytes=max_file_bytes,
        )

        if not dl_res.success:
            storm_res["status"] = "FAILED"
            storm_res["error"] = dl_res.error_message
            report["failed"] += 1
            report["storm_results"].append(storm_res)
            continue

        if dl_res.was_cached:
            report["already_cached"] += 1
            storm_res["status"] = "ALREADY_CACHED"
        else:
            report["downloaded"] += 1
            report["total_bytes_downloaded"] += dl_res.file_size_bytes
            current_download_bytes += dl_res.file_size_bytes
            storm_res["status"] = "DOWNLOADED"

        storm_res["file_size_bytes"] = dl_res.file_size_bytes
        storm_res["sha256"] = dl_res.checksum_sha256

        # Unpack .nc files into storm_raw_dir
        extracted_files = []
        try:
            with tarfile.open(local_tar_path, "r:gz") as tar:
                for member in tar.getmembers():
                    if member.name.startswith("/") or ".." in member.name:
                        continue
                    if member.name.endswith(".nc"):
                        dest_file = os.path.join(storm_raw_dir, member.name)
                        if os.path.exists(dest_file):
                            try:
                                import stat
                                os.chmod(dest_file, stat.S_IWRITE)
                            except OSError:
                                pass
                        tar.extract(member, path=storm_raw_dir)
                        if os.path.exists(dest_file):
                            try:
                                import stat
                                os.chmod(dest_file, stat.S_IWRITE)
                            except OSError:
                                pass
                        extracted_files.append(member.name)
            storm_res["extracted_nc_count"] = len(extracted_files)
            report["total_netcdf_files_extracted"] += len(extracted_files)
        except Exception as e:
            storm_res["status"] = "CORRUPTED"
            storm_res["error"] = f"Extraction failed: {str(e)}"
            report["corrupted"] += 1

        report["storm_results"].append(storm_res)

    # Save report
    os.makedirs(os.path.dirname(os.path.abspath(output_report_path)), exist_ok=True)
    with open(output_report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return report


if __name__ == "__main__":
    rep = execute_bounded_hursat_download()
    print("=== Download Report ===")
    print(f"Discovered: {rep['discovered']}")
    print(f"Attempted: {rep['attempted']}")
    print(f"Downloaded: {rep['downloaded']}")
    print(f"Already cached: {rep['already_cached']}")
    print(f"Skipped: {rep['skipped']}")
    print(f"Failed: {rep['failed']}")
    print(f"Corrupted: {rep['corrupted']}")
    print(f"Total downloaded bytes: {rep['total_bytes_downloaded'] / (1024*1024):.2f} MB")
    print(f"Total NetCDF files extracted: {rep['total_netcdf_files_extracted']}")
    for s in rep["storm_results"]:
        print(f" - {s['storm_id']} {s['storm_name']}: {s['status']}, {s['extracted_nc_count']} .nc files")
