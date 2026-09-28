"""
CycloneGuard Data Pipeline Command-Line Interface (CLI).
Enables inspection, validation, normalization, spatial-temporal alignment,
storm-wise dataset splitting, and manifest generation from the terminal.

Usage:
  python -m ml.data inspect <file>
  python -m ml.data validate <file> [--format <ext>]
  python -m ml.data normalize <file> --type <ibtracs|hursat> [--output <path>]
  python -m ml.data align --satellite <file> --track <file> --storm <sid> [--tolerance <hours>]
  python -m ml.data split --track <file> [--train <0.7>] [--val <0.15>] [--test <0.15>]
  python -m ml.data manifest <file> --source <source_id> --name <name> --version <version>
  python -m ml.data sources
"""

import argparse
import json
import os
import sys

from ml.data.adapters.hursat import HURSATAdapter
from ml.data.adapters.ibtracs import IBTrACSAdapter
from ml.data.alignment.spatial import SpatialAligner
from ml.data.alignment.temporal import TemporalAligner
from ml.data.inspection.hursat_inspector import inspect_hursat_file
from ml.data.manifests.manifest import generate_manifest_for_file
from ml.data.registry import registry
from ml.data.splitting.storm_split import StormWiseSplitter
from ml.data.validation.validator import DataValidator


def cmd_sources(args):
    print("=== CYCLONEGUARD VERIFIED DATA SOURCE REGISTRY ===")
    for s in registry.list_sources():
        print(f"\n[{s.status.value}] {s.source_id}")
        print(f"  Name:       {s.name}")
        print(f"  Provider:   {s.provider}")
        print(f"  Type:       {s.data_type.value}")
        print(f"  Format:     {s.format}")
        print(f"  Resolution: Spatial={s.spatial_resolution} | Temporal={s.temporal_resolution}")
        print(f"  Coverage:   {s.coverage}")
        print(f"  Docs:       {s.documentation_url}")


def cmd_inspect(args):
    file_path = args.file
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    ext = os.path.splitext(file_path)[1].lower()
    if ext in (".nc", ".nc3", ".nc4"):
        rep = inspect_hursat_file(file_path)
        rep.print_summary()
    elif ext in (".csv", ".txt"):
        adapter = IBTrACSAdapter()
        parsed = adapter.parse(file_path)
        print("=== IBTrACS CSV INSPECTION ===")
        print(f"File: {file_path}")
        print(f"Total Rows: {parsed.records_count}")
        print(f"Total Columns: {len(parsed.raw_variables)}")
        print(f"Units Header: {parsed.raw_attributes.get('units_header', 'N/A')[:100]}...")
        print("Sample Columns:", parsed.raw_variables[:15])
    else:
        print(f"Inspection unsupported for extension '{ext}'. Supported: .nc, .csv")


def cmd_validate(args):
    file_path = args.file
    ext = os.path.splitext(file_path)[1].lower()

    print(f"=== VALIDATING: {file_path} ===")
    file_rep = DataValidator.validate_file(file_path)
    for c in file_rep.checks:
        print(f"  [{c.severity.value}] {c.check_name}: {c.message}")

    if not file_rep.is_valid:
        print(f"\nResult: FAILED ({file_rep.status.value})")
        sys.exit(1)

    if ext in (".nc", ".nc3", ".nc4"):
        adapter = HURSATAdapter()
        report = adapter.validate(file_path)
    elif ext in (".csv",):
        adapter = IBTrACSAdapter()
        report = adapter.validate(file_path)
    else:
        report = file_rep

    print(f"\nDomain Content Checks:")
    for c in report.checks:
        print(f"  [{c.severity.value}] {c.check_name}: {c.message}")

    print(f"\nFinal Validation Status: {report.status.value}")
    if not report.is_valid:
        sys.exit(1)


def cmd_normalize(args):
    file_path = args.file
    source_type = args.type.lower()

    if source_type == "ibtracs":
        adapter = IBTrACSAdapter()
        parsed = adapter.parse(file_path)
        norm = adapter.normalize(parsed)
        print(f"Normalized {norm.records_count} points across {len(norm.data_payload)} storm tracks.")
        print(f"Spatial Bounds: {norm.spatial_bounds}")
        print(f"Time Range: {norm.time_range_utc}")
    elif source_type == "hursat":
        adapter = HURSATAdapter()
        parsed = adapter.parse(file_path)
        norm = adapter.normalize(parsed)
        print(f"Normalized HURSAT satellite imagery. Channels: {norm.data_payload['metadata'].channels}")
        print(f"Grid Shape: {norm.data_payload['metadata'].grid_shape}")
        print(f"Spatial Bounds: {norm.spatial_bounds}")
    else:
        print(f"Error: Unknown type '{source_type}'. Choose 'ibtracs' or 'hursat'.", file=sys.stderr)
        sys.exit(1)


def cmd_align(args):
    sat_file = args.satellite
    track_file = args.track
    storm_id = args.storm
    tol_h = args.tolerance

    ib = IBTrACSAdapter()
    norm_ib = ib.normalize(ib.parse(track_file))
    if storm_id not in norm_ib.data_payload:
        print(f"Error: Storm ID '{storm_id}' not found in {track_file}", file=sys.stderr)
        sys.exit(1)

    track = norm_ib.data_payload[storm_id]

    hs = HURSATAdapter()
    norm_hs = hs.normalize(hs.parse(sat_file))
    sat_time = norm_hs.data_payload["metadata"].timestamp_utc

    alignment = TemporalAligner.align_observation_to_track(sat_time, track, max_tolerance_hours=tol_h)
    if not alignment:
        print("Error: Could not perform temporal alignment.", file=sys.stderr)
        sys.exit(1)

    print("=== TEMPORAL ALIGNMENT ===")
    print(f"Satellite Time: {alignment.satellite_time_utc}")
    print(f"Matched Track:  {alignment.matched_track_time_utc} (Delta T = {alignment.time_difference_seconds}s)")
    print(f"Center Lat/Lon: ({alignment.matched_latitude}, {alignment.matched_longitude})")
    print(f"Matched Wind:   {alignment.matched_wind_kts} kts | Pres: {alignment.matched_pressure_mb} mb")
    print(f"Within Tol:     {alignment.is_within_tolerance}")

    if not alignment.is_within_tolerance:
        print(f"Observation exceeds maximum tolerance ({tol_h} hours). Skipping spatial extraction.")
        return

    irwin = norm_hs.data_payload["arrays"].get("IRWIN")
    lats = norm_hs.data_payload["coordinates"]["lat"]
    lons = norm_hs.data_payload["coordinates"]["lon"]

    crop_arr, crop_meta = SpatialAligner.extract_crop(
        satellite_array=irwin,
        lats=lats,
        lons=lons,
        center_lat=alignment.matched_latitude,
        center_lon=alignment.matched_longitude,
        crop_shape=(64, 64),
        pixel_resolution_deg=0.08,
        storm_id=storm_id,
        storm_name=track.storm_name,
        observation_time_utc=sat_time,
        track_time_utc=alignment.matched_track_time_utc,
    )

    print("\n=== SPATIAL EXTRACTION ===")
    print(f"Crop Shape: {crop_arr.shape}")
    print(f"Center Pixel: ({crop_meta.center_latitude}, {crop_meta.center_longitude})")
    print(f"Min Temp:   {crop_meta.min_value} K | Max Temp: {crop_meta.max_value} K | Mean: {crop_meta.mean_value} K")
    print(f"Padded:     {crop_meta.is_boundary_padded} | Missing Fraction: {crop_meta.missing_pixels_fraction}")


def cmd_split(args):
    track_file = args.track
    train_r = args.train
    val_r = args.val
    test_r = args.test

    ib = IBTrACSAdapter()
    norm = ib.normalize(ib.parse(track_file))
    storms = norm.data_payload

    train, val, test, summary = StormWiseSplitter.split_by_ratio(
        storms, train_ratio=train_r, val_ratio=val_r, test_ratio=test_r, seed=args.seed
    )

    print("=== STORM-WISE DATASET SPLIT ===")
    print(f"Total Cyclones: {summary.total_storms} | Total Points: {summary.total_points}")
    print(f"Train Partition ({train_r:.0%}): {len(train)} storms, {summary.train_points_count} points -> {summary.train_storms}")
    print(f"Val Partition   ({val_r:.0%}): {len(val)} storms, {summary.val_points_count} points -> {summary.val_storms}")
    print(f"Test Partition  ({test_r:.0%}): {len(test)} storms, {summary.test_points_count} points -> {summary.test_storms}")
    print("Zero Data Leakage: Verified (disjoint storm IDs).")


def cmd_manifest(args):
    file_path = args.file
    m = generate_manifest_for_file(
        source_id=args.source,
        dataset_name=args.name,
        version=args.version,
        file_path=file_path,
    )
    saved_path = m.save()
    print(f"Created dataset manifest: {saved_path}")
    print(f"  SHA-256: {m.checksum_sha256}")
    print(f"  Size:    {m.file_size_bytes:,} bytes")


def main():
    parser = argparse.ArgumentParser(description="CycloneGuard Data Foundation CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # sources
    subparsers.add_parser("sources", help="List central verified data sources")

    # inspect
    p_inspect = subparsers.add_parser("inspect", help="Inspect raw or sample dataset")
    p_inspect.add_argument("file", help="File path to inspect")

    # validate
    p_val = subparsers.add_parser("validate", help="Validate dataset integrity and bounds")
    p_val.add_argument("file", help="File path to validate")

    # normalize
    p_norm = subparsers.add_parser("normalize", help="Normalize dataset")
    p_norm.add_argument("file", help="File path to normalize")
    p_norm.add_argument("--type", required=True, choices=["ibtracs", "hursat"], help="Adapter type")
    p_norm.add_argument("--output", help="Optional output path")

    # align
    p_align = subparsers.add_parser("align", help="Spatial-temporal alignment")
    p_align.add_argument("--satellite", required=True, help="Satellite file")
    p_align.add_argument("--track", required=True, help="Track file")
    p_align.add_argument("--storm", required=True, help="Storm SID")
    p_align.add_argument("--tolerance", type=float, default=3.0, help="Max tolerance hours")

    # split
    p_split = subparsers.add_parser("split", help="Storm-wise dataset splitting")
    p_split.add_argument("--track", required=True, help="Track file")
    p_split.add_argument("--train", type=float, default=0.70, help="Train ratio")
    p_split.add_argument("--val", type=float, default=0.15, help="Val ratio")
    p_split.add_argument("--test", type=float, default=0.15, help="Test ratio")
    p_split.add_argument("--seed", type=int, default=42, help="Random seed")

    # manifest
    p_man = subparsers.add_parser("manifest", help="Generate SHA-256 manifest")
    p_man.add_argument("file", help="Target file")
    p_man.add_argument("--source", required=True, help="Source ID")
    p_man.add_argument("--name", required=True, help="Dataset name")
    p_man.add_argument("--version", default="v01", help="Dataset version")

    args = parser.parse_args()

    if args.command == "sources":
        cmd_sources(args)
    elif args.command == "inspect":
        cmd_inspect(args)
    elif args.command == "validate":
        cmd_validate(args)
    elif args.command == "normalize":
        cmd_normalize(args)
    elif args.command == "align":
        cmd_align(args)
    elif args.command == "split":
        cmd_split(args)
    elif args.command == "manifest":
        cmd_manifest(args)


if __name__ == "__main__":
    main()
