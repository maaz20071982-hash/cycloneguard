"""
Phase 1: Historical Target Storms Inventory Generator.
Extracts verified North Indian Ocean tropical cyclones from NOAA IBTrACS NI archive
spanning multiple seasons (2013-2015) with valid tracks, timestamps, coordinates,
and intensity records suitable for RI labeling.
"""

import csv
import json
import os
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Any


TARGET_STORM_IDS = [
    "2013281N12098",  # PHAILIN (2013, BB)
    "2013322N13090",  # HELEN (2013, BB)
    "2014279N11096",  # HUDHUD (2014, BB)
    "2014297N11062",  # NILOFAR (2014, AS)
    "2015301N11065",  # CHAPALA (2015, AS)
    "2015309N14067",  # MEGH (2015, AS)
]


def build_historical_target_storms_manifest(
    ibtracs_csv_path: str,
    output_manifest_path: str,
    target_storm_ids: List[str] = TARGET_STORM_IDS,
) -> Dict[str, Any]:
    """Parses target storms from IBTrACS and constructs historical_target_storms.json."""
    if not os.path.exists(ibtracs_csv_path):
        raise FileNotFoundError(f"IBTrACS file not found: {ibtracs_csv_path}")

    storms_data = defaultdict(list)
    with open(ibtracs_csv_path, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        headers = next(reader)
        units = next(reader)

        sid_idx = headers.index("SID")
        season_idx = headers.index("SEASON")
        name_idx = headers.index("NAME")
        iso_time_idx = headers.index("ISO_TIME")
        lat_idx = headers.index("LAT")
        lon_idx = headers.index("LON")
        wind_idx = headers.index("WMO_WIND")
        pres_idx = headers.index("WMO_PRES")
        nature_idx = headers.index("NATURE")
        basin_idx = headers.index("BASIN")
        subbasin_idx = headers.index("SUBBASIN")

        for row in reader:
            if not row or len(row) <= sid_idx:
                continue
            sid = row[sid_idx].strip()
            if sid in target_storm_ids:
                iso_time = row[iso_time_idx].strip()
                lat_str = row[lat_idx].strip()
                lon_str = row[lon_idx].strip()
                wind_str = row[wind_idx].strip()
                pres_str = row[pres_idx].strip()

                try:
                    lat_val = float(lat_str) if lat_str and lat_str != " " else None
                    lon_val = float(lon_str) if lon_str and lon_str != " " else None
                except ValueError:
                    lat_val, lon_val = None, None

                try:
                    wind_val = float(wind_str) if wind_str and wind_str != " " else None
                except ValueError:
                    wind_val = None

                try:
                    pres_val = float(pres_str) if pres_str and pres_str != " " else None
                except ValueError:
                    pres_val = None

                storms_data[sid].append({
                    "iso_time": iso_time,
                    "latitude": lat_val,
                    "longitude": lon_val,
                    "wind_speed_kts": wind_val,
                    "central_pressure_mb": pres_val,
                    "nature": row[nature_idx].strip(),
                    "basin": row[basin_idx].strip(),
                    "subbasin": row[subbasin_idx].strip(),
                    "storm_name": row[name_idx].strip(),
                    "season": int(row[season_idx].strip()),
                })

    target_inventory = []
    total_track_obs = 0

    for sid in target_storm_ids:
        obs = storms_data.get(sid, [])
        if not obs:
            continue
        
        # Sort chronologically
        obs.sort(key=lambda x: x["iso_time"])
        sname = obs[0]["storm_name"]
        season = obs[0]["season"]
        subbasin = obs[0]["subbasin"]
        start_time = obs[0]["iso_time"]
        end_time = obs[-1]["iso_time"]
        n_obs = len(obs)
        total_track_obs += n_obs

        # Find min/max valid wind
        valid_winds = [o["wind_speed_kts"] for o in obs if o["wind_speed_kts"] is not None]
        max_wind = max(valid_winds) if valid_winds else None
        min_pres = min([o["central_pressure_mb"] for o in obs if o["central_pressure_mb"] is not None], default=None)

        # Expected HURSAT matching window is start_time - 3h to end_time + 3h
        t_start_dt = datetime.fromisoformat(start_time.replace(" ", "T"))
        t_end_dt = datetime.fromisoformat(end_time.replace(" ", "T"))

        target_inventory.append({
            "storm_id": sid,
            "storm_name": sname,
            "season": season,
            "basin": "NI",
            "subbasin": subbasin,
            "start_time_utc": f"{start_time.replace(' ', 'T')}Z",
            "end_time_utc": f"{end_time.replace(' ', 'T')}Z",
            "number_of_track_observations": n_obs,
            "max_wind_kts": max_wind,
            "min_pressure_mb": min_pres,
            "expected_hursat_matching_window": {
                "window_start_utc": t_start_dt.isoformat() + "Z",
                "window_end_utc": t_end_dt.isoformat() + "Z",
                "temporal_tolerance_minutes": 30.0,
            },
            "tarball_pattern": f"HURSAT_b1_v06_{sid}_{sname}*.tar.gz",
        })

    manifest = {
        "manifest_version": "1.0.0",
        "created_at_utc": datetime.utcnow().isoformat() + "Z",
        "source": "NOAA IBTrACS v04r01 (North Indian Ocean)",
        "total_target_storms": len(target_inventory),
        "total_track_observations": total_track_obs,
        "seasons_represented": sorted(list(set(t["season"] for t in target_inventory))),
        "subbasins_represented": sorted(list(set(t["subbasin"] for t in target_inventory))),
        "target_storms": target_inventory,
    }

    os.makedirs(os.path.dirname(os.path.abspath(output_manifest_path)), exist_ok=True)
    with open(output_manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return manifest


if __name__ == "__main__":
    ibtracs_csv = "data/raw/ibtracs/ibtracs.NI.list.v04r01.csv"
    out_json = "data/manifests/historical_target_storms.json"
    manifest = build_historical_target_storms_manifest(ibtracs_csv, out_json)
    print(f"Generated {out_json}")
    print(f"Target storms: {manifest['total_target_storms']}")
    print(f"Total track observations: {manifest['total_track_observations']}")
    for s in manifest["target_storms"]:
        print(f" - {s['storm_id']} ({s['season']}) {s['storm_name']}: {s['number_of_track_observations']} fixes [{s['start_time_utc']} to {s['end_time_utc']}]")
