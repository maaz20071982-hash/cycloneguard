"""
Spatial Cyclone-Centered Crop Extraction Engine for CycloneGuard.
Extracts normalized spatial patches centered on tropical cyclone circulation centers.
Features:
- Configurable crop dimensions (e.g. 128x128 pixels).
- Configurable spatial resolution in degrees (e.g. 0.08° ~ 8.8 km).
- Proper boundary padding with NaNs when cyclone center is near grid boundaries.
- Precision coordinate verification: storm center maps directly to center pixel.
- Detailed metadata preservation.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from ml.data.schemas.satellite import CycloneCenteredCrop


class SpatialAligner:
    """Extracts storm-centered satellite tensor crops from 2D and 3D imagery."""

    @staticmethod
    def extract_crop(
        satellite_array: np.ndarray,
        lats: np.ndarray,
        lons: np.ndarray,
        center_lat: float,
        center_lon: float,
        crop_shape: Tuple[int, int] = (64, 64),
        pixel_resolution_deg: float = 0.08,
        storm_id: str = "UNKNOWN",
        storm_name: Optional[str] = None,
        observation_time_utc: str = "",
        track_time_utc: str = "",
        source_id: str = "hursat",
        channels: Optional[List[str]] = None,
        time_diff_seconds: float = 0.0,
    ) -> Tuple[np.ndarray, CycloneCenteredCrop]:
        """
        Extracts a cyclone-centered square crop of size (crop_height, crop_width).
        Center pixel is located at (crop_height // 2, crop_width // 2).
        Returns:
            (crop_array, crop_metadata)
        """
        crop_h, crop_w = crop_shape
        half_h = crop_h // 2
        half_w = crop_w // 2

        # Create target coordinate grids centered at (center_lat, center_lon)
        # Latitudes ascend South to North: center_lat - half_h * res to center_lat + half_h * res
        target_lats = center_lat + (np.arange(crop_h) - half_h) * pixel_resolution_deg
        target_lons = center_lon + (np.arange(crop_w) - half_w) * pixel_resolution_deg

        # Determine dimensions of input array
        is_multi_channel = satellite_array.ndim == 3
        if is_multi_channel:
            n_channels = satellite_array.shape[0]
            out_crop = np.full((n_channels, crop_h, crop_w), np.nan, dtype=np.float32)
        else:
            n_channels = 1
            out_crop = np.full((crop_h, crop_w), np.nan, dtype=np.float32)

        is_padded = False

        # Input grid spacing
        lat_step = (lats[-1] - lats[0]) / (len(lats) - 1) if len(lats) > 1 else 1.0
        lon_step = (lons[-1] - lons[0]) / (len(lons) - 1) if len(lons) > 1 else 1.0

        lat_min, lat_max = min(lats[0], lats[-1]), max(lats[0], lats[-1])
        lon_min, lon_max = min(lons[0], lons[-1]), max(lons[0], lons[-1])

        # Map each target pixel to the nearest source pixel
        for i, t_lat in enumerate(target_lats):
            for j, t_lon in enumerate(target_lons):
                # Check boundary
                if not (lat_min <= t_lat <= lat_max and lon_min <= t_lon <= lon_max):
                    is_padded = True
                    continue

                # Nearest neighbor index in source
                src_i = int(round((t_lat - lats[0]) / lat_step))
                src_j = int(round((t_lon - lons[0]) / lon_step))

                if 0 <= src_i < len(lats) and 0 <= src_j < len(lons):
                    if is_multi_channel:
                        out_crop[:, i, j] = satellite_array[:, src_i, src_j]
                    else:
                        out_crop[i, j] = satellite_array[src_i, src_j]
                else:
                    is_padded = True

        total_pixels = out_crop.size
        nan_pixels = int(np.isnan(out_crop).sum())
        nan_fraction = nan_pixels / total_pixels if total_pixels > 0 else 0.0

        valid_vals = out_crop[~np.isnan(out_crop)]
        min_val = float(np.min(valid_vals)) if valid_vals.size > 0 else None
        max_val = float(np.max(valid_vals)) if valid_vals.size > 0 else None
        mean_val = float(np.mean(valid_vals)) if valid_vals.size > 0 else None

        meta = CycloneCenteredCrop(
            storm_id=storm_id,
            storm_name=storm_name,
            observation_time_utc=observation_time_utc,
            track_time_utc=track_time_utc,
            center_latitude=round(center_lat, 4),
            center_longitude=round(center_lon, 4),
            crop_height=crop_h,
            crop_width=crop_w,
            pixel_resolution_deg=pixel_resolution_deg,
            channels=channels or ["IRWIN"],
            source_id=source_id,
            time_difference_seconds=round(time_diff_seconds, 2),
            is_boundary_padded=is_padded,
            missing_pixels_count=nan_pixels,
            missing_pixels_fraction=round(nan_fraction, 4),
            quality_flag="PADDED" if is_padded else ("DEGRADED" if nan_fraction > 0.1 else "NOMINAL"),
            array_shape=out_crop.shape,
            min_value=round(min_val, 2) if min_val is not None else None,
            max_value=round(max_val, 2) if max_val is not None else None,
            mean_value=round(mean_val, 2) if mean_val is not None else None,
        )

        return out_crop, meta
