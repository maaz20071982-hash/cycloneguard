"""
CLI Tool: Run Cyclone-Centered Patch Extraction on verified coincident satellite files.

Usage:
    python -m ml.data.preprocessing.extract_patches
"""

import json
import os
import sys

from ml.data.adapters.ibtracs import IBTrACSAdapter
from ml.data.manifests.satellite_manifest import SatelliteManifestStore
from ml.data.alignment.coincidence_engine import CoincidenceEngine
from ml.data.preprocessing.patch_extractor import CyclonePatchExtractor


def main():
    print("=== CYCLONEGUARD SATELLITE PATCH EXTRACTION ===")
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

    # 1. Load IBTrACS tracks
    ibtracs_csv = os.path.join(root_dir, "data", "samples", "ibtracs_sample_ni.csv")
    if not os.path.exists(ibtracs_csv):
        print(f"Error: IBTrACS sample not found at {ibtracs_csv}", file=sys.stderr)
        sys.exit(1)

    adapter = IBTrACSAdapter()
    parsed = adapter.parse(ibtracs_csv)
    norm = adapter.normalize(parsed)
    series_map = norm.data_payload  # Dict[sid, CycloneTrackSeries]

    all_points = [p for s in series_map.values() for p in s.points]
    print(f"Loaded {len(all_points)} track points across {len(series_map)} cyclones.")

    # 2. Load satellite manifests
    manifest_store = SatelliteManifestStore()
    manifests = manifest_store.read_records()
    print(f"Loaded {len(manifests)} satellite manifest records.")

    # 3. Match and extract patches
    engine = CoincidenceEngine()
    extractor = CyclonePatchExtractor()

    extracted_count = 0
    for m in manifests:
        full_path = os.path.join(root_dir, m.file_path) if not os.path.isabs(m.file_path) else m.file_path
        if not os.path.exists(full_path):
            print(f"Warning: File not found {full_path}", file=sys.stderr)
            continue

        storm_points = [p for p in all_points if p.storm_id == m.storm_id]
        for pt in storm_points:
            match = engine.match_asset_to_track_point(pt, m)
            if match.available:
                print(f"Coincident match found! Storm: {pt.storm_name} ({pt.storm_id}) at {pt.timestamp_utc}")
                print(f"  Satellite Time: {match.satellite_time_utc} | Delta: {match.delta_minutes:.1f} min")
                results = extractor.extract_and_save_patch(
                    nc_file_path=full_path,
                    track_point=pt,
                    source_id=m.source,
                    channels=m.channels,
                )
                for pfile, meta in results:
                    rel_p = os.path.relpath(pfile, root_dir)
                    print(f"  -> Extracted patch [{meta.channel}]: {rel_p} ({meta.crop_shape[0]}x{meta.crop_shape[1]}, Status: {meta.quality_status})")
                    extracted_count += 1

    print(f"\nExtraction complete. Total patches saved: {extracted_count}")


if __name__ == "__main__":
    main()
