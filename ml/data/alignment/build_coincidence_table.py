"""
Central Multimodal Coincidence Table Generator for CycloneGuard.
Sprint 7 - Phase 7 Deliverable.

Unites IBTrACS best-track observations with multi-source satellite assets
(Infrared, Microwave, Scatterometer) into a single canonical table.
Outputs:
- data/processed/multi_source_coincidence.csv
- data/processed/multi_source_coincidence.jsonl

Usage:
    python -m ml.data.alignment.build_coincidence_table
"""

import csv
import json
import os
import sys
from typing import Dict, List, Optional

from ml.data.adapters.ibtracs import IBTrACSAdapter
from ml.data.alignment.coincidence_engine import (
    CoincidenceEngine,
    MultiSourceCoincidenceRow,
    TemporalCoincidenceToleranceConfig,
)
from ml.data.manifests.satellite_manifest import SatelliteManifestStore


def load_partition_map(split_config_path: str) -> Dict[str, str]:
    """Loads storm ID to partition mapping from split_config.json."""
    if not os.path.exists(split_config_path):
        return {}
    with open(split_config_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    p_map = {}
    for sid in data.get("train_storms", []):
        p_map[sid] = "TRAIN"
    for sid in data.get("val_storms", []):
        p_map[sid] = "VAL"
    for sid in data.get("test_storms", []):
        p_map[sid] = "TEST"
    return p_map


def build_and_save_coincidence_table(
    ibtracs_csv: str,
    output_dir: str,
    split_config_path: str,
    tolerances: Optional[TemporalCoincidenceToleranceConfig] = None,
) -> List[MultiSourceCoincidenceRow]:
    """Generates the master multimodal observation table."""
    adapter = IBTrACSAdapter()
    parsed = adapter.parse(ibtracs_csv)
    norm = adapter.normalize(parsed)
    series_map = norm.data_payload

    all_points = [p for s in series_map.values() for p in s.points]
    all_points.sort(key=lambda p: (p.storm_id, p.timestamp_utc))

    manifest_store = SatelliteManifestStore()
    manifests = manifest_store.read_records()
    partition_map = load_partition_map(split_config_path)

    engine = CoincidenceEngine(tolerances)
    rows = engine.build_multimodal_coincidence_table(
        track_points=all_points,
        satellite_manifests=manifests,
        partition_map=partition_map,
    )

    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, "multi_source_coincidence.csv")
    jsonl_path = os.path.join(output_dir, "multi_source_coincidence.jsonl")

    # Write CSV
    fieldnames = [
        "storm_id",
        "storm_name",
        "cyclone_time_utc",
        "latitude",
        "longitude",
        "wind_speed_kts",
        "central_pressure_mb",
        "nature",
        "partition",
        "ir_available",
        "ir_asset_id",
        "ir_file_path",
        "ir_time_utc",
        "ir_delta_minutes",
        "ir_quality",
        "microwave_available",
        "microwave_asset_id",
        "microwave_file_path",
        "microwave_time_utc",
        "microwave_delta_minutes",
        "microwave_quality",
        "scatterometer_available",
        "scatterometer_asset_id",
        "scatterometer_file_path",
        "scatterometer_time_utc",
        "scatterometer_delta_minutes",
        "scatterometer_quality",
        "total_coincident_sources",
        "coincidence_quality",
        "coincidence_flags",
    ]

    with open(csv_path, "w", newline="", encoding="utf-8") as f_csv:
        writer = csv.DictWriter(f_csv, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            d = r.model_dump()
            d["coincidence_flags"] = ";".join(d["coincidence_flags"])
            writer.writerow(d)

    # Write JSONL
    with open(jsonl_path, "w", encoding="utf-8") as f_jsonl:
        for r in rows:
            f_jsonl.write(json.dumps(r.model_dump()) + "\n")

    return rows


def main():
    print("=== BUILDING MULTI-SOURCE COINCIDENCE TABLE ===")
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    ibtracs_csv = os.path.join(root_dir, "data", "samples", "ibtracs_sample_ni.csv")
    output_dir = os.path.join(root_dir, "data", "processed")
    split_config_path = os.path.join(root_dir, "ml", "config", "split_config.json")

    rows = build_and_save_coincidence_table(
        ibtracs_csv=ibtracs_csv,
        output_dir=output_dir,
        split_config_path=split_config_path,
    )

    total = len(rows)
    ir_matches = sum(1 for r in rows if r.ir_available)
    mw_matches = sum(1 for r in rows if r.microwave_available)
    scat_matches = sum(1 for r in rows if r.scatterometer_available)
    multi_matches = sum(1 for r in rows if r.total_coincident_sources > 1)

    print(f"Total Cyclone Observations: {total}")
    print(f"IR Coincident Matches:       {ir_matches} ({ir_matches / total * 100:.2f}%)")
    print(f"Microwave Matches:           {mw_matches} ({mw_matches / total * 100:.2f}%)")
    print(f"Scatterometer Matches:       {scat_matches} ({scat_matches / total * 100:.2f}%)")
    print(f"Multimodal (>= 2 sources):   {multi_matches} ({multi_matches / total * 100:.2f}%)")
    print(f"Output CSV saved to:   {os.path.join(output_dir, 'multi_source_coincidence.csv')}")
    print(f"Output JSONL saved to: {os.path.join(output_dir, 'multi_source_coincidence.jsonl')}")


if __name__ == "__main__":
    main()
