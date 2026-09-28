"""
Cyclone-Centered Satellite Patch Extraction Engine.
Sprint 7 - Phase 5 & Phase 6 Deliverables.

Extracts normalized spatial patches centered on tropical cyclone centers.
Guarantees:
1. Reusable patch extraction organized by:
   data/processed/satellite_patches/{storm_id}/{timestamp}/{source}/{channel}/
2. Preserves original scientific values in float32 (e.g. Kelvin, albedo). No destructive clipping or 8-bit quantization.
3. Accompanies every patch.npy with metadata.json recording spatial bounds, timestamps, delta_minutes, and quality flags.
"""

from datetime import datetime, timezone
import json
import os
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from pydantic import BaseModel, Field

from ml.data.io.netcdf3 import NetCDF3Dataset
from ml.data.schemas.track import CycloneTrackPoint


class PatchMetadata(BaseModel):
    """Metadata saved alongside patch.npy."""
    storm_id: str
    storm_name: Optional[str] = None
    cyclone_time: str
    satellite_time: str
    delta_minutes: float
    latitude: float
    longitude: float
    source: str
    channel: str
    spatial_extent: List[float]  # [lat_min, lat_max, lon_min, lon_max]
    resolution_deg: float
    resolution_km: float
    crop_shape: List[int]
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    mean_value: Optional[float] = None
    nan_count: int = 0
    nan_fraction: float = 0.0
    quality_flags: List[str] = Field(default_factory=list)
    quality_status: str = "NOMINAL"  # NOMINAL, PADDED, DEGRADED, REJECTED
    units: str = "Kelvin"
    created_at_utc: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class CyclonePatchExtractor:
    """Extracts cyclone-centered scientific patches from satellite grids."""

    def __init__(
        self,
        crop_shape: Tuple[int, int] = (64, 64),
        pixel_resolution_deg: float = 0.08,
        output_base_dir: Optional[str] = None,
    ):
        self.crop_shape = crop_shape
        self.pixel_resolution_deg = pixel_resolution_deg
        if output_base_dir is None:
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
            output_base_dir = os.path.join(root_dir, "data", "processed", "satellite_patches")
        self.output_base_dir = output_base_dir

    def extract_patch_array(
        self,
        satellite_grid: np.ndarray,
        lats: np.ndarray,
        lons: np.ndarray,
        center_lat: float,
        center_lon: float,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Extracts a 2D patch of size crop_shape centered on (center_lat, center_lon).
        Preserves original float32 scientific values.
        """
        crop_h, crop_w = self.crop_shape
        half_h = crop_h // 2
        half_w = crop_w // 2

        target_lats = center_lat + (np.arange(crop_h) - half_h) * self.pixel_resolution_deg
        target_lons = center_lon + (np.arange(crop_w) - half_w) * self.pixel_resolution_deg

        patch = np.full((crop_h, crop_w), np.nan, dtype=np.float32)
        is_padded = False

        lat_step = (lats[-1] - lats[0]) / (len(lats) - 1) if len(lats) > 1 else 1.0
        lon_step = (lons[-1] - lons[0]) / (len(lons) - 1) if len(lons) > 1 else 1.0

        lat_min, lat_max = min(lats[0], lats[-1]), max(lats[0], lats[-1])
        lon_min, lon_max = min(lons[0], lons[-1]), max(lons[0], lons[-1])

        for i, t_lat in enumerate(target_lats):
            for j, t_lon in enumerate(target_lons):
                if not (lat_min <= t_lat <= lat_max and lon_min <= t_lon <= lon_max):
                    is_padded = True
                    continue

                src_i = int(round((t_lat - lats[0]) / lat_step))
                src_j = int(round((t_lon - lons[0]) / lon_step))

                if 0 <= src_i < len(lats) and 0 <= src_j < len(lons):
                    patch[i, j] = satellite_grid[src_i, src_j]
                else:
                    is_padded = True

        nan_count = int(np.isnan(patch).sum())
        total_pixels = patch.size
        nan_frac = nan_count / total_pixels if total_pixels > 0 else 0.0

        valid_vals = patch[~np.isnan(patch)]
        min_val = float(np.min(valid_vals)) if valid_vals.size > 0 else None
        max_val = float(np.max(valid_vals)) if valid_vals.size > 0 else None
        mean_val = float(np.mean(valid_vals)) if valid_vals.size > 0 else None

        flags = []
        if is_padded:
            flags.append("BOUNDARY_PADDED")
        if nan_frac > 0.5:
            q_status = "REJECTED"
            flags.append("EXCESSIVE_NANS_GT_50_PCT")
        elif nan_frac > 0.1:
            q_status = "DEGRADED"
            flags.append("HIGH_NANS_GT_10_PCT")
        elif is_padded:
            q_status = "PADDED"
        else:
            q_status = "NOMINAL"

        spatial_extent = [
            float(round(target_lats[0], 4)),
            float(round(target_lats[-1], 4)),
            float(round(target_lons[0], 4)),
            float(round(target_lons[-1], 4)),
        ]

        metrics = {
            "spatial_extent": spatial_extent,
            "min_val": round(min_val, 2) if min_val is not None else None,
            "max_val": round(max_val, 2) if max_val is not None else None,
            "mean_val": round(mean_val, 2) if mean_val is not None else None,
            "nan_count": nan_count,
            "nan_fraction": round(nan_frac, 4),
            "quality_flags": flags,
            "quality_status": q_status,
        }

        return patch, metrics

    def extract_and_save_patch(
        self,
        nc_file_path: str,
        track_point: CycloneTrackPoint,
        source_id: str = "noaa_hursat_b1",
        channels: Optional[List[str]] = None,
    ) -> List[Tuple[str, PatchMetadata]]:
        """
        Extracts patches for all requested channels from a NetCDF file,
        saving patch.npy and metadata.json under:
        {output_base_dir}/{storm_id}/{timestamp_slug}/{source}/{channel}/
        """
        if not os.path.exists(nc_file_path):
            raise FileNotFoundError(f"Satellite file not found: {nc_file_path}")

        ds = NetCDF3Dataset(nc_file_path, mode="r")
        atts = dict(ds.attributes)
        vars_dict = ds.variables

        sat_time = atts.get("time_coverage_start") or atts.get("time") or track_point.timestamp_utc
        # Calculate delta minutes
        t_cyclone = datetime.fromisoformat(track_point.timestamp_utc.replace("Z", "+00:00"))
        t_sat = datetime.fromisoformat(sat_time.replace("Z", "+00:00"))
        if t_cyclone.tzinfo is None:
            t_cyclone = t_cyclone.replace(tzinfo=timezone.utc)
        if t_sat.tzinfo is None:
            t_sat = t_sat.replace(tzinfo=timezone.utc)
        delta_min = round((t_sat - t_cyclone).total_seconds() / 60.0, 2)

        lat_var = vars_dict.get("lat") or vars_dict.get("latitude")
        lon_var = vars_dict.get("lon") or vars_dict.get("longitude")
        if lat_var is None or lon_var is None:
            raise ValueError(f"Missing spatial coordinates in {nc_file_path}")

        lats = lat_var.data
        lons = lon_var.data

        avail_channels = [c for c in (channels or ["IRWIN", "IRWVP", "VSCHN"]) if c in vars_dict]
        saved_outputs = []

        time_slug = track_point.timestamp_utc.replace(":", "").replace("-", "")

        for ch in avail_channels:
            raw_grid = vars_dict[ch].data
            patch_arr, metrics = self.extract_patch_array(
                satellite_grid=raw_grid,
                lats=lats,
                lons=lons,
                center_lat=track_point.latitude,
                center_lon=track_point.longitude,
            )

            # Determine units
            if ch in ("IRWIN", "IRWVP"):
                ch_units = "Kelvin (Brightness Temperature)"
            elif ch == "VSCHN":
                ch_units = "Albedo Fraction [0..1]"
            else:
                ch_units = "Raw Calibrated Units"

            meta = PatchMetadata(
                storm_id=track_point.storm_id,
                storm_name=track_point.storm_name,
                cyclone_time=track_point.timestamp_utc,
                satellite_time=sat_time,
                delta_minutes=delta_min,
                latitude=track_point.latitude,
                longitude=track_point.longitude,
                source=source_id,
                channel=ch,
                spatial_extent=metrics["spatial_extent"],
                resolution_deg=self.pixel_resolution_deg,
                resolution_km=round(self.pixel_resolution_deg * 111.0, 1),
                crop_shape=list(self.crop_shape),
                min_value=metrics["min_val"],
                max_value=metrics["max_val"],
                mean_value=metrics["mean_val"],
                nan_count=metrics["nan_count"],
                nan_fraction=metrics["nan_fraction"],
                quality_flags=metrics["quality_flags"],
                quality_status=metrics["quality_status"],
                units=ch_units,
            )

            # Target directory
            ch_dir = os.path.join(
                self.output_base_dir,
                track_point.storm_id,
                time_slug,
                source_id,
                ch,
            )
            os.makedirs(ch_dir, exist_ok=True)

            patch_file = os.path.join(ch_dir, "patch.npy")
            meta_file = os.path.join(ch_dir, "metadata.json")

            np.save(patch_file, patch_arr)
            with open(meta_file, "w", encoding="utf-8") as f:
                json.dump(meta.model_dump(), f, indent=2)

            saved_outputs.append((patch_file, meta))

        return saved_outputs
