"""
CLI tool: Inspect all candidate satellite sources and report data readiness levels.

Usage:
    python -m ml.data.acquisition.inspect_sources
"""

import sys
from ml.data.acquisition.registry import source_registry


def main():
    print("================================================================================")
    print("           CYCLONEGUARD SATELLITE DATA SOURCE INVENTORY & READINESS             ")
    print("================================================================================")

    sources = source_registry.list_sources()
    print(f"Total candidate sources audited: {len(sources)}\n")

    for s in sources:
        status_tag = f"[{s.current_integration_status.value}]"
        print(f"{status_tag:<22} {s.source_id}")
        print(f"  Name:             {s.source_name}")
        print(f"  Provider:         {s.provider}")
        print(f"  Sensor:           {s.sensor}")
        print(f"  Type:             {s.sensor_type.value}")
        print(f"  Channels:         {', '.join(s.channels)}")
        print(f"  Resolution:       Spatial={s.spatial_resolution} | Temporal={s.temporal_resolution}")
        print(f"  Coverage:         {s.geographic_coverage}")
        print(f"  Years Available:  {s.available_years}")
        print(f"  Format:           {s.file_format}")
        print(f"  Access:           {s.access_method}")
        print(f"  Auto Retrieval:   {s.automated_retrieval_possible}")
        print(f"  Local Staged:     {s.current_local_availability} ({s.local_files_count} files, {s.total_observations_local} obs)")
        if s.notes:
            print(f"  Scientific Notes: {s.notes}")
        print("-" * 80)


if __name__ == "__main__":
    main()
