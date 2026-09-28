"""
CLI tool: Build or update the machine-readable satellite asset manifest (satellite_manifest.jsonl).
Scans data directories for valid satellite files (NetCDF), extracts metadata,
validates integrity, and records provenance.

Usage:
    python -m ml.data.acquisition.build_manifest
"""

import glob
import os
import sys
from typing import List
import numpy as np

from ml.data.adapters.base import BaseDataSourceAdapter
from ml.data.io.netcdf3 import NetCDF3Dataset
from ml.data.manifests.satellite_manifest import (
    SatelliteAssetManifestRecord,
    SatelliteManifestStore,
)


def scan_and_catalog_satellite_files() -> List[SatelliteAssetManifestRecord]:
    """Scans data/raw/ and data/samples/ for verified satellite NetCDF files."""
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    search_dirs = [
        os.path.join(root_dir, "data", "samples"),
        os.path.join(root_dir, "data", "raw", "hursat"),
    ]

    records: List[SatelliteAssetManifestRecord] = []
    seen_checksums = set()

    for sdir in search_dirs:
        if not os.path.exists(sdir):
            continue
        nc_files = glob.glob(os.path.join(sdir, "**", "*.nc*"), recursive=True)
        for fpath in nc_files:
            try:
                ds = NetCDF3Dataset(fpath, mode="r")
                atts = dict(ds.attributes)
                dims = dict(ds.dimensions)
                vars_dict = ds.variables

                # Extract metadata
                sid = atts.get("storm_id") or atts.get("SID")
                if not sid or sid == "UNKNOWN":
                    parent_dir = os.path.basename(os.path.dirname(fpath))
                    if parent_dir.startswith("20"):
                        sid = parent_dir
                    else:
                        sid = os.path.basename(fpath).split(".")[0]

                sname = atts.get("storm_name") or atts.get("NAME")
                if not sname or sname == "UNNAMED":
                    parts = os.path.basename(fpath).split(".")
                    if len(parts) > 1 and len(parts[1]) >= 3:
                        sname = parts[1]
                    else:
                        sname = "UNNAMED"

                time_iso = atts.get("time_coverage_start") or atts.get("time") or "UNKNOWN"
                if time_iso != "UNKNOWN" and not time_iso.endswith("Z") and "+" not in time_iso:
                    time_iso = time_iso + "Z"

                # Check channels
                channels = [c for c in ("IRWIN", "IRWVP", "VSCHN") if c in vars_dict]
                primary_channel = "IRWIN" if "IRWIN" in channels else (channels[0] if channels else "UNKNOWN")

                # Coordinate bounds
                lat_var = vars_dict.get("lat") or vars_dict.get("latitude")
                lon_var = vars_dict.get("lon") or vars_dict.get("longitude")

                if lat_var is not None and lon_var is not None:
                    lats = lat_var.data
                    lons = lon_var.data
                    cov = {
                        "lat_min": float(np.nanmin(lats)),
                        "lat_max": float(np.nanmax(lats)),
                        "lon_min": float(np.nanmin(lons)),
                        "lon_max": float(np.nanmax(lons)),
                    }
                    res_deg = float(round(abs(lats[1] - lats[0]), 4)) if len(lats) > 1 else 0.08
                    dim_list = [int(len(lats)), int(len(lons))]
                else:
                    cov = {"lat_min": 0.0, "lat_max": 0.0, "lon_min": 0.0, "lon_max": 0.0}
                    res_deg = 0.08
                    dim_list = []

                size_bytes = os.path.getsize(fpath)
                sha256 = BaseDataSourceAdapter.compute_sha256(fpath)

                if sha256 in seen_checksums:
                    continue
                seen_checksums.add(sha256)

                # Quality checks
                flags = []
                status = "VALID"
                if primary_channel in vars_dict:
                    ir_data = vars_dict[primary_channel].data
                    nan_count = int(np.isnan(ir_data).sum())
                    total_pix = ir_data.size
                    nan_frac = nan_count / total_pix if total_pix > 0 else 0.0
                    if nan_frac > 0.5:
                        status = "REJECTED"
                        flags.append("EXCESSIVE_NANS_GT_50_PCT")
                    elif nan_frac > 0.1:
                        status = "DEGRADED"
                        flags.append("HIGH_NANS_GT_10_PCT")

                rel_path = os.path.relpath(fpath, root_dir).replace("\\", "/")
                asset_id = f"hursat_b1_{sid}_{time_iso.replace(':', '').replace('-', '')}"

                record = SatelliteAssetManifestRecord(
                    asset_id=asset_id,
                    source="noaa_hursat_b1",
                    product="HURSAT-B1",
                    sensor="ISCCP-B1 Geostationary Composite",
                    channel=primary_channel,
                    channels=channels,
                    timestamp=time_iso,
                    storm_id=sid,
                    storm_name=sname,
                    file_path=rel_path,
                    file_size=size_bytes,
                    checksum=sha256,
                    coverage=cov,
                    spatial_resolution_deg=res_deg,
                    dimensions=dim_list,
                    processing_level="L2",
                    status=status,
                    quality_flags=flags,
                    metadata={
                        "spatial_resolution_km": 8.0,
                        "units": "Kelvin (IRWIN)",
                        "satellite": atts.get("satellite", "ISCCP-B1 Composite"),
                    },
                )
                records.append(record)

            except Exception as e:
                print(f"Warning: Failed to parse satellite candidate {fpath}: {e}", file=sys.stderr)

    return records


def main():
    print("=== BUILDING SATELLITE ASSET MANIFEST ===")
    records = scan_and_catalog_satellite_files()
    print(f"Found {len(records)} valid satellite assets.")

    store = SatelliteManifestStore()
    store.write_records(records)
    print(f"Manifest written to: {store.manifest_file}")

    for r in records:
        print(f"  [{r.status}] {r.asset_id} | Storm: {r.storm_id} ({r.storm_name}) | Time: {r.timestamp} | Chans: {r.channels} | Size: {r.file_size} B")


if __name__ == "__main__":
    main()
