"""
CycloneGuard Environmental Data Acquisition & Extraction Engine.
Sprint 10 Deliverable.

Fetches and caches real, authoritative atmospheric and oceanic reanalysis data
for historical cyclone observations:
1. NOAA PSL NCEP/DOE Reanalysis 2 (R2) 4-times daily (6-hourly) pressure level
   winds (850 hPa, 200 hPa) and relative humidity (700 hPa, 500 hPa).
2. NOAA PSL High-Resolution Optimum Interpolation Sea Surface Temperature (OISST v2.0 highres).

Features:
- Robust local file caching in `data/interim/environmental_cache/`.
- Persistent OPeNDAP NetCDF dataset handle management.
- Zero data fabrication; explicit missingness flags for unobserved / land cells.
- Directional causality enforcement (t_env <= t_obs, zero future lookahead).
"""

from datetime import datetime, timezone, timedelta
import json
import math
import os
import time
from typing import Any, Dict, List, Optional, Tuple
import netCDF4
import numpy as np
import pandas as pd

from ml.features.environmental import (
    EnvironmentalFeatureExtractor,
    EnvironmentalObservation,
    ENVIRONMENTAL_FEATURE_NAMES,
)


class EnvironmentalFetcher:
    """Manages acquisition, caching, and extraction of environmental features."""

    def __init__(self, project_root: str, cache_dir: Optional[str] = None):
        self.project_root = project_root
        self.cache_dir = cache_dir or os.path.join(project_root, "data", "interim", "environmental_cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        self._datasets: Dict[str, netCDF4.Dataset] = {}

    def _get_dataset(self, url: str, max_retries: int = 3, backoff: float = 2.0) -> Optional[netCDF4.Dataset]:
        """Caches open netCDF4 OPeNDAP dataset handles with retry logic."""
        if url in self._datasets:
            return self._datasets[url]

        for attempt in range(max_retries):
            try:
                ds = netCDF4.Dataset(url)
                self._datasets[url] = ds
                return ds
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"[EnvironmentalFetcher] Failed to open {url}: {e}")
                    return None
                time.sleep(backoff * (attempt + 1))
        return None

    def close(self) -> None:
        """Closes all cached NetCDF datasets."""
        for url, ds in self._datasets.items():
            try:
                ds.close()
            except Exception:
                pass
        self._datasets.clear()

    def get_observation_environmental_data(
        self,
        storm_id: str,
        storm_name: str,
        iso_time: str,
        lat: float,
        lon: float,
    ) -> EnvironmentalObservation:
        """
        Retrieves environmental data for one cyclone fix, using disk cache if available.
        Strictly guarantees directional causality (t_env <= t_obs).
        """
        # Format cache filename
        time_slug = iso_time.replace(":", "").replace("-", "")
        storm_cache_dir = os.path.join(self.cache_dir, storm_id)
        os.makedirs(storm_cache_dir, exist_ok=True)
        cache_file = os.path.join(storm_cache_dir, f"{time_slug}.json")

        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cached = json.load(f)
                return EnvironmentalObservation(
                    wind_speed_850hpa_kmh=cached.get("w850_kmh"),
                    wind_direction_850hpa_deg=cached.get("d850_deg"),
                    wind_speed_200hpa_kmh=cached.get("w200_kmh"),
                    wind_direction_200hpa_deg=cached.get("d200_deg"),
                    relative_humidity_700hpa_pct=cached.get("rh700"),
                    relative_humidity_500hpa_pct=cached.get("rh500"),
                    sst_celsius=cached.get("sst"),
                    dt_minutes=float(cached.get("dt_minutes", 0.0)),
                )
            except Exception:
                pass

        dt = datetime.fromisoformat(iso_time.replace("Z", "+00:00"))
        year = dt.year

        # 1. Enforce strict directional causality for atmospheric reanalysis (t_env <= t_obs)
        # 6-hourly synoptic steps: 00, 06, 12, 18 UTC.
        synoptic_hour = math.floor(dt.hour / 6) * 6
        dt_synoptic = datetime(year, dt.month, dt.day, synoptic_hour, 0, tzinfo=timezone.utc)
        dt_minutes = (dt - dt_synoptic).total_seconds() / 60.0

        # Synoptic time index in NCEP R2 (4 steps per day from Jan 1 00:00 UTC)
        year_start = datetime(year, 1, 1, 0, 0, tzinfo=timezone.utc)
        r2_time_idx = int(round((dt_synoptic - year_start).total_seconds() / (6 * 3600.0)))

        # NCEP R2 spatial coordinates:
        # Lat: 90.0 to -90.0 in 2.5 deg steps (73 pts)
        r2_lat_idx = max(0, min(72, int(round((90.0 - lat) / 2.5))))
        # Lon: 0.0 to 357.5 in 2.5 deg steps (144 pts)
        r2_lon_idx = max(0, min(143, int(round((lon % 360.0) / 2.5))))

        # 2. Fetch atmospheric variables from NCEP R2 via OPeNDAP
        url_u = f"https://psl.noaa.gov/thredds/dodsC/Datasets/ncep.reanalysis2/pressure/uwnd.{year}.nc"
        url_v = f"https://psl.noaa.gov/thredds/dodsC/Datasets/ncep.reanalysis2/pressure/vwnd.{year}.nc"
        url_rh = f"https://psl.noaa.gov/thredds/dodsC/Datasets/ncep.reanalysis2/pressure/rhum.{year}.nc"

        ds_u = self._get_dataset(url_u)
        ds_v = self._get_dataset(url_v)
        ds_rh = self._get_dataset(url_rh)

        w850_kmh, d850_deg = None, None
        w200_kmh, d200_deg = None, None
        rh700, rh500 = None, None

        if ds_u and ds_v:
            try:
                # Level 2 = 850 hPa, Level 9 = 200 hPa
                u850 = float(ds_u.variables["uwnd"][r2_time_idx, 2, r2_lat_idx, r2_lon_idx])
                u200 = float(ds_u.variables["uwnd"][r2_time_idx, 9, r2_lat_idx, r2_lon_idx])
                v850 = float(ds_v.variables["vwnd"][r2_time_idx, 2, r2_lat_idx, r2_lon_idx])
                v200 = float(ds_v.variables["vwnd"][r2_time_idx, 9, r2_lat_idx, r2_lon_idx])

                # Check missing value (-9.96921e36)
                if abs(u850) < 1000.0 and abs(v850) < 1000.0:
                    w850_ms = math.sqrt(u850 * u850 + v850 * v850)
                    w850_kmh = w850_ms * 3.6
                    d850_deg = (math.degrees(math.atan2(-u850, -v850)) + 360.0) % 360.0

                if abs(u200) < 1000.0 and abs(v200) < 1000.0:
                    w200_ms = math.sqrt(u200 * u200 + v200 * v200)
                    w200_kmh = w200_ms * 3.6
                    d200_deg = (math.degrees(math.atan2(-u200, -v200)) + 360.0) % 360.0
            except Exception as e:
                print(f"[EnvironmentalFetcher] Error extracting wind for {storm_id} {iso_time}: {e}")

        if ds_rh:
            try:
                # Level 3 = 700 hPa, Level 5 = 500 hPa
                rh700_raw = float(ds_rh.variables["rhum"][r2_time_idx, 3, r2_lat_idx, r2_lon_idx])
                rh500_raw = float(ds_rh.variables["rhum"][r2_time_idx, 5, r2_lat_idx, r2_lon_idx])
                if 0.0 <= rh700_raw <= 100.0:
                    rh700 = rh700_raw
                if 0.0 <= rh500_raw <= 100.0:
                    rh500 = rh500_raw
            except Exception as e:
                print(f"[EnvironmentalFetcher] Error extracting RH for {storm_id} {iso_time}: {e}")

        # 3. Fetch Sea Surface Temperature from NOAA PSL OISST v2.0 highres
        url_sst = f"https://psl.noaa.gov/thredds/dodsC/Datasets/noaa.oisst.v2.highres/sst.day.mean.{year}.nc"
        ds_sst = self._get_dataset(url_sst)
        sst_celsius = None

        if ds_sst:
            try:
                # Daily index
                day_idx = (dt.date() - datetime(year, 1, 1).date()).days
                # Lat: -89.875 to 89.875 in 0.25 deg steps (720 pts)
                sst_lat_idx = max(0, min(719, int(round((lat - (-89.875)) / 0.25))))
                # Lon: 0.125 to 359.875 in 0.25 deg steps (1440 pts)
                sst_lon_idx = max(0, min(1439, int(round(((lon % 360.0) - 0.125) / 0.25))))

                sst_raw = float(ds_sst.variables["sst"][day_idx, sst_lat_idx, sst_lon_idx])
                # Filter land / masked cells (masked as -9.96921e36 or < 0 for tropical waters)
                if 0.0 <= sst_raw <= 45.0:
                    sst_celsius = sst_raw
                else:
                    sst_celsius = None
            except Exception as e:
                print(f"[EnvironmentalFetcher] Error extracting SST for {storm_id} {iso_time}: {e}")

        # Save to disk cache
        cache_dict = {
            "storm_id": storm_id,
            "storm_name": storm_name,
            "iso_time": iso_time,
            "latitude": lat,
            "longitude": lon,
            "w850_kmh": w850_kmh,
            "d850_deg": d850_deg,
            "w200_kmh": w200_kmh,
            "d200_deg": d200_deg,
            "rh700": rh700,
            "rh500": rh500,
            "sst": sst_celsius,
            "dt_minutes": dt_minutes,
            "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache_dict, f, indent=2)

        return EnvironmentalObservation(
            wind_speed_850hpa_kmh=w850_kmh,
            wind_direction_850hpa_deg=d850_deg,
            wind_speed_200hpa_kmh=w200_kmh,
            wind_direction_200hpa_deg=d200_deg,
            relative_humidity_700hpa_pct=rh700,
            relative_humidity_500hpa_pct=rh500,
            sst_celsius=sst_celsius,
            dt_minutes=dt_minutes,
        )

    def extract_environmental_dataset(
        self,
        samples_df: pd.DataFrame,
        output_csv_path: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Iterates over all cyclone fixes in samples_df, extracts environmental features,
        computes antecedent shear tendencies, and returns a paired DataFrame.
        """
        print(f"[EnvironmentalFetcher] Beginning environmental ingestion for {len(samples_df)} cyclone observations...")
        rows: List[Dict[str, Any]] = []

        # Sort by storm_id and cyclone_time_utc to ensure chronological ordering
        df_sorted = samples_df.sort_values(by=["storm_id", "cyclone_time_utc"]).copy()

        # Group by storm to compute 6h antecedent shear
        for storm_id, grp in df_sorted.groupby("storm_id"):
            storm_obs: List[Tuple[str, EnvironmentalObservation, Optional[float]]] = []
            storm_name = str(grp["storm_name"].iloc[0])
            print(f"[EnvironmentalFetcher] Ingesting storm {storm_name} ({storm_id}), {len(grp)} fixes...")

            for _, r in grp.iterrows():
                t_curr = str(r["cyclone_time_utc"])
                lat = float(r["latitude"])
                lon = float(r["longitude"])
                name = str(r["storm_name"])

                obs = self.get_observation_environmental_data(
                    storm_id=storm_id,
                    storm_name=name,
                    iso_time=t_curr,
                    lat=lat,
                    lon=lon,
                )

                # Calculate shear for current observation
                vws_mag, _, _, _ = EnvironmentalFeatureExtractor.calculate_shear(
                    obs.wind_speed_850hpa_kmh,
                    obs.wind_direction_850hpa_deg,
                    obs.wind_speed_200hpa_kmh,
                    obs.wind_direction_200hpa_deg,
                )

                # Find 6h prior shear
                dt_curr = datetime.fromisoformat(t_curr.replace("Z", "+00:00"))
                prior_shear = None
                for prev_time, prev_obs, prev_vws in reversed(storm_obs):
                    dt_prev = datetime.fromisoformat(prev_time.replace("Z", "+00:00"))
                    diff_hours = (dt_curr - dt_prev).total_seconds() / 3600.0
                    if 4.5 <= diff_hours <= 7.5 and prev_vws is not None:
                        prior_shear = prev_vws
                        break
                    elif diff_hours > 8.0:
                        break

                obs.prior_vws_magnitude_kts = prior_shear
                feats = EnvironmentalFeatureExtractor.extract_features(obs)

                # Assemble complete row record
                row_record = {
                    "storm_id": storm_id,
                    "storm_name": name,
                    "cyclone_time_utc": t_curr,
                    "latitude": lat,
                    "longitude": lon,
                    "partition": str(r.get("partition", "")),
                    "ri_target": r.get("ri_target"),
                    "ri_label_status": str(r.get("ri_label_status", "")),
                }
                row_record.update(feats)
                rows.append(row_record)

                storm_obs.append((t_curr, obs, vws_mag))

        self.close()

        res_df = pd.DataFrame(rows)
        if output_csv_path:
            os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
            res_df.to_csv(output_csv_path, index=False)
            print(f"[EnvironmentalFetcher] Successfully saved {len(res_df)} environmental rows to {output_csv_path}")

        return res_df
