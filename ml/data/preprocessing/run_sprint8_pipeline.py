"""
Sprint 8 Central Pipeline:
Executes:
1. IBTrACS Historical Track Ingestion (6 Target Storms, 347 Points)
2. Coincidence Matching with HURSAT-B1 Satellite Assets
3. Cyclone-Centered Multi-Channel Patch Extraction (IRWIN, IRWVP, VSCHN)
4. Forward Rapid Intensification (RI) Ground-Truth Labeling (24h, >= 30 kts)
5. Generation of canonical data products:
   - data/processed/hursat_coincidence_table.csv
   - data/processed/hursat_coincidence_table.jsonl
   - data/processed/hursat_ri_samples.csv
"""

from collections import Counter, defaultdict
import csv
from datetime import datetime
import json
import os
import sys
from typing import Any, Dict, List, Optional

from ml.data.adapters.ibtracs import IBTrACSAdapter
from ml.data.alignment.coincidence_engine import (
    CoincidenceEngine,
    MultiSourceCoincidenceRow,
    TemporalCoincidenceToleranceConfig,
)
from ml.data.manifests.satellite_manifest import SatelliteManifestStore
from ml.data.preprocessing.patch_extractor import CyclonePatchExtractor, PatchMetadata
from ml.data.sequences.ri_label import RILabelGenerator, RILabelResult


def load_historical_partition_map(split_config_path: str) -> Dict[str, str]:
    """Loads storm ID to partition mapping from split config."""
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


def run_sprint8_processing_pipeline(
    ibtracs_csv: str = "data/processed/ibtracs_historical_targets.csv",
    split_config_path: str = "ml/config/historical_split_config.json",
    patch_output_dir: str = "data/processed/satellite_patches",
    output_processed_dir: str = "data/processed",
) -> Dict[str, Any]:
    """Executes full historical matching, patch extraction, and RI labeling."""
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

    # 1. Parse and normalize IBTrACS tracks
    adapter = IBTrACSAdapter()
    parsed = adapter.parse(ibtracs_csv)
    norm = adapter.normalize(parsed)
    series_map = norm.data_payload

    all_points = [p for s in series_map.values() for p in s.points]
    all_points.sort(key=lambda p: (p.storm_id, p.timestamp_utc))
    pt_map = {(p.storm_id, p.timestamp_utc): p for p in all_points}

    # 2. Load Satellite Manifests
    manifest_store = SatelliteManifestStore()
    manifests = manifest_store.read_records()
    partition_map = load_historical_partition_map(split_config_path)

    # 3. Match in space and time
    engine = CoincidenceEngine()
    rows: List[MultiSourceCoincidenceRow] = engine.build_multimodal_coincidence_table(
        track_points=all_points,
        satellite_manifests=manifests,
        partition_map=partition_map,
    )

    # 4. Extract Cyclone-Centered Patches
    extractor = CyclonePatchExtractor(output_base_dir=patch_output_dir)
    extracted_patch_records = []
    patch_stats_by_storm = defaultdict(lambda: {"extracted_patches": 0, "channels": Counter()})

    for row in rows:
        if row.ir_available and row.ir_file_path:
            full_nc = os.path.join(root_dir, row.ir_file_path) if not os.path.isabs(row.ir_file_path) else row.ir_file_path
            pt = pt_map.get((row.storm_id, row.cyclone_time_utc))
            if pt and os.path.exists(full_nc):
                try:
                    patch_outputs = extractor.extract_and_save_patch(
                        nc_file_path=full_nc,
                        track_point=pt,
                        source_id="noaa_hursat_b1",
                        channels=["IRWIN", "IRWVP", "VSCHN"],
                    )
                    for pfile, meta in patch_outputs:
                        extracted_patch_records.append((pfile, meta))
                        patch_stats_by_storm[row.storm_id]["extracted_patches"] += 1
                        patch_stats_by_storm[row.storm_id]["channels"][meta.channel] += 1
                except Exception as e:
                    print(f"Warning: Failed patch extraction for {row.storm_id} at {row.cyclone_time_utc}: {e}", file=sys.stderr)

    # 5. Generate Forward RI Ground-Truth Labels & Supervised Dataset
    os.makedirs(output_processed_dir, exist_ok=True)
    ri_samples_csv = os.path.join(output_processed_dir, "hursat_ri_samples.csv")
    coinc_csv = os.path.join(output_processed_dir, "hursat_coincidence_table.csv")
    coinc_jsonl = os.path.join(output_processed_dir, "hursat_coincidence_table.jsonl")

    ri_rows = []
    ri_counts_by_partition = defaultdict(lambda: {"total": 0, "available": 0, "ri_pos": 0, "ri_neg": 0, "unavail": 0})
    ri_counts_by_storm = defaultdict(lambda: {"total": 0, "available": 0, "ri_pos": 0, "ri_neg": 0, "unavail": 0})

    for row in rows:
        pt = pt_map.get((row.storm_id, row.cyclone_time_utc))
        series = series_map.get(row.storm_id)
        if not pt or not series:
            continue

        ri_res: RILabelResult = RILabelGenerator.generate_label(
            current_point=pt,
            track_series=series,
            horizon_hours=24.0,
            threshold_kts=30.0,
            tolerance_hours=3.0,
        )

        time_slug = row.cyclone_time_utc.replace(":", "").replace("-", "")
        patch_dir_rel = os.path.join("data", "processed", "satellite_patches", row.storm_id, time_slug, "noaa_hursat_b1").replace("\\", "/")

        part = row.partition
        ri_counts_by_partition[part]["total"] += 1
        ri_counts_by_storm[row.storm_id]["total"] += 1

        is_avail = (ri_res.status == "AVAILABLE")
        if is_avail:
            ri_counts_by_partition[part]["available"] += 1
            ri_counts_by_storm[row.storm_id]["available"] += 1
            if ri_res.is_ri:
                ri_target = 1
                ri_counts_by_partition[part]["ri_pos"] += 1
                ri_counts_by_storm[row.storm_id]["ri_pos"] += 1
            else:
                ri_target = 0
                ri_counts_by_partition[part]["ri_neg"] += 1
                ri_counts_by_storm[row.storm_id]["ri_neg"] += 1
        else:
            ri_target = None
            ri_counts_by_partition[part]["unavail"] += 1
            ri_counts_by_storm[row.storm_id]["unavail"] += 1

        ri_row = {
            "storm_id": row.storm_id,
            "storm_name": row.storm_name,
            "cyclone_time_utc": row.cyclone_time_utc,
            "latitude": row.latitude,
            "longitude": row.longitude,
            "current_wind_kts": row.wind_speed_kts,
            "central_pressure_mb": row.central_pressure_mb,
            "nature": row.nature,
            "partition": row.partition,
            "satellite_source": "noaa_hursat_b1",
            "satellite_file": row.ir_file_path,
            "satellite_time_utc": row.ir_time_utc,
            "delta_minutes": row.ir_delta_minutes,
            "patch_dir": patch_dir_rel,
            "ir_quality": row.ir_quality,
            "target_time_utc": ri_res.target_time_utc,
            "future_wind_kts": ri_res.future_wind_kts,
            "delta_wind_kts": ri_res.delta_wind_kts,
            "ri_horizon_hours": ri_res.horizon_hours,
            "ri_threshold_kts": ri_res.threshold_kts,
            "is_future_track_valid": is_avail,
            "ri_label_status": ri_res.status,
            "ri_target": ri_target if ri_target is not None else "",
            "justification": ri_res.justification,
        }
        ri_rows.append(ri_row)

    # 6. Write hursat_ri_samples.csv
    ri_fieldnames = list(ri_rows[0].keys())
    with open(ri_samples_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ri_fieldnames)
        writer.writeheader()
        writer.writerows(ri_rows)

    # 7. Write Coincidence Tables (CSV & JSONL)
    coinc_fieldnames = [
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

    with open(coinc_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=coinc_fieldnames)
        writer.writeheader()
        for r in rows:
            d = r.model_dump()
            d["coincidence_flags"] = ";".join(d["coincidence_flags"])
            writer.writerow(d)

    with open(coinc_jsonl, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r.model_dump()) + "\n")

    summary = {
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "total_storms": len(series_map),
        "total_track_observations": len(all_points),
        "matched_observations": sum(1 for r in rows if r.ir_available),
        "match_rate_pct": round(sum(1 for r in rows if r.ir_available) / len(all_points) * 100.0, 2),
        "total_extracted_patches": len(extracted_patch_records),
        "total_supervised_24h_samples": sum(p["available"] for p in ri_counts_by_partition.values()),
        "total_ri_positive_samples": sum(p["ri_pos"] for p in ri_counts_by_partition.values()),
        "total_ri_negative_samples": sum(p["ri_neg"] for p in ri_counts_by_partition.values()),
        "partition_metrics": dict(ri_counts_by_partition),
        "storm_metrics": dict(ri_counts_by_storm),
        "patch_stats_by_storm": {sid: dict(stats) for sid, stats in patch_stats_by_storm.items()},
        "outputs": {
            "hursat_ri_samples_csv": ri_samples_csv,
            "hursat_coincidence_csv": coinc_csv,
            "hursat_coincidence_jsonl": coinc_jsonl,
            "patch_dir": patch_output_dir,
        },
    }

    return summary


if __name__ == "__main__":
    print("=== EXECUTING SPRINT 8 HISTORICAL EXPANSION PIPELINE ===")
    res = run_sprint8_processing_pipeline()
    print("\n=== PIPELINE EXECUTION SUMMARY ===")
    print(f"Target Storms:                 {res['total_storms']}")
    print(f"Total Track Observations:      {res['total_track_observations']}")
    print(f"Matched Observations:          {res['matched_observations']} ({res['match_rate_pct']}%)")
    print(f"Total Patches Extracted:       {res['total_extracted_patches']}")
    print(f"Supervised 24h Samples:        {res['total_supervised_24h_samples']}")
    print(f"RI Positive Events:            {res['total_ri_positive_samples']}")
    print(f"RI Negative Events:            {res['total_ri_negative_samples']}")
    print("\nBy Partition:")
    for part, stats in res["partition_metrics"].items():
        prev = (stats['ri_pos'] / stats['available'] * 100.0) if stats['available'] > 0 else 0.0
        print(f"  [{part}] Track Fixes: {stats['total']}, Supervised: {stats['available']}, RI+: {stats['ri_pos']}, RI-: {stats['ri_neg']} (Prevalence: {prev:.2f}%)")
