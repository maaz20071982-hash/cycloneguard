"""
Phase 2: HURSAT Archive Discovery.
Systematically discovers available historical HURSAT-B1 v06 archive assets from NOAA NCEI,
verifies remote locations, gets file sizes via HTTP HEAD requests, maps against target storms,
and writes data/manifests/hursat_archive_inventory.jsonl.
"""

import json
import os
import re
import urllib.request
from typing import Dict, List, Any, Optional

from ml.data.acquisition.adapters.hursat import HURSATAcquisitionAdapter
from ml.data.acquisition.config import default_config


def discover_and_build_inventory(
    target_manifest_path: str = "data/manifests/historical_target_storms.json",
    output_inventory_path: str = "data/manifests/hursat_archive_inventory.jsonl",
) -> List[Dict[str, Any]]:
    """Discovers HURSAT archive assets and outputs inventory JSONL."""
    with open(target_manifest_path, "r", encoding="utf-8") as f:
        target_data = json.load(f)

    target_sids = {s["storm_id"]: s for s in target_data["target_storms"]}
    years = target_data["seasons_represented"]

    adapter = HURSATAcquisitionAdapter(default_config)
    inventory_records = []

    for yr in years:
        year_url = f"{adapter.archive_url}{yr}/"
        try:
            req = urllib.request.Request(
                year_url,
                headers={"User-Agent": default_config.user_agent},
            )
            with urllib.request.urlopen(req, timeout=default_config.timeout_seconds) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
                pattern = r'href=["\'](HURSAT_b1_v06_([0-9]{4}[0-9]{3}[NS][0-9]{5})_([A-Za-z0-9_-]+)_c[0-9]+\.tar\.gz)["\']'
                matches = re.findall(pattern, html)

                for full_fname, sid, sname in matches:
                    is_target = sid in target_sids
                    remote_url = f"{year_url}{full_fname}"
                    
                    # For target storms, get exact remote size via HEAD request
                    expected_size = None
                    if is_target:
                        try:
                            head_req = urllib.request.Request(
                                remote_url,
                                method="HEAD",
                                headers={"User-Agent": default_config.user_agent},
                            )
                            with urllib.request.urlopen(head_req, timeout=10) as head_resp:
                                cl = head_resp.headers.get("Content-Length")
                                if cl:
                                    expected_size = int(cl)
                        except Exception:
                            expected_size = None

                    # Check local cache status
                    local_storm_dir = os.path.join(default_config.raw_data_dir, "hursat", sid)
                    local_tar = os.path.join(local_storm_dir, full_fname)
                    is_cached = os.path.exists(local_tar) and os.path.getsize(local_tar) > 0

                    record = {
                        "source": "noaa_hursat_b1",
                        "product": "HURSAT-B1 v06",
                        "year": yr,
                        "asset_identifier": f"HURSAT_b1_v06_{sid}_{sname}",
                        "file_name": full_fname,
                        "storm_id": sid,
                        "storm_name": target_sids[sid]["storm_name"] if is_target else sname,
                        "remote_location": remote_url,
                        "expected_size_bytes": expected_size,
                        "metadata_status": "VERIFIED" if is_target else "UNINDEXED",
                        "download_status": "ALREADY_CACHED" if is_cached else "DISCOVERED",
                        "is_target_storm": is_target,
                        "local_cache_path": local_tar if is_cached else None,
                    }
                    inventory_records.append(record)

        except Exception as e:
            print(f"Failed to query {year_url}: {e}")

    # Write JSONL
    os.makedirs(os.path.dirname(os.path.abspath(output_inventory_path)), exist_ok=True)
    with open(output_inventory_path, "w", encoding="utf-8") as f:
        for rec in inventory_records:
            f.write(json.dumps(rec) + "\n")

    return inventory_records


if __name__ == "__main__":
    records = discover_and_build_inventory()
    target_recs = [r for r in records if r["is_target_storm"]]
    print(f"Total discovered assets across target years: {len(records)}")
    print(f"Target storm assets: {len(target_recs)}")
    for tr in target_recs:
        size_mb = (tr['expected_size_bytes'] / (1024*1024)) if tr['expected_size_bytes'] else 0
        print(f" - {tr['storm_id']} ({tr['year']}) {tr['storm_name']}: {size_mb:.2f} MB, status: {tr['download_status']}")
