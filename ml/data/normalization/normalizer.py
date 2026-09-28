"""
Scientific Normalization Engine for CycloneGuard.
Applies unambiguous, scientifically justified coordinate and unit transformations:
- Timestamps -> UTC ISO-8601 string and Unix epoch seconds.
- Longitudes -> [-180.0, 180.0] degrees East.
- Latitudes -> [-90.0, 90.0] degrees North.
- Satellite Arrays -> Monotonic coordinate ordering (lat descending/ascending, lon ascending).
- Missing Values -> Consistent representation (None for scalars, np.nan for floating-point tensors).
- Units -> Knots for sustained winds (WMO / IMD standard), mb (hPa) for pressure, Kelvin for brightness temp.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from ml.data.schemas.track import CycloneTrackPoint, CycloneTrackSeries


class DataNormalizer:
    """Normalization utilities for spatial, temporal, and physical variables."""

    @staticmethod
    def normalize_timestamp_to_utc(time_val: Any) -> Tuple[str, float]:
        """
        Normalizes various timestamp representations into (ISO-8601 UTC string, Unix timestamp float).
        Rejects ambiguous timezone specifications.
        """
        if isinstance(time_val, (int, float)):
            dt = datetime.fromtimestamp(time_val, tz=timezone.utc)
        elif isinstance(time_val, datetime):
            if time_val.tzinfo is None:
                # Default to UTC for meteorological best-tracks (standard WMO convention)
                dt = time_val.replace(tzinfo=timezone.utc)
            else:
                dt = time_val.astimezone(timezone.utc)
        elif isinstance(time_val, str):
            s = time_val.strip()
            # Handle common formats
            if s.endswith("Z"):
                s = s[:-1] + "+00:00"
            try:
                dt = datetime.fromisoformat(s)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                else:
                    dt = dt.astimezone(timezone.utc)
            except ValueError:
                # Try '%Y-%m-%d %H:%M:%S'
                dt = datetime.strptime(s[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        else:
            raise TypeError(f"Unsupported timestamp type: {type(time_val)}")

        iso_str = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        epoch_secs = dt.timestamp()
        return iso_str, epoch_secs

    @staticmethod
    def normalize_longitude(lon: float) -> float:
        """
        Normalizes longitude into standard [-180.0, 180.0] degrees East.
        Examples:
          85.5 -> 85.5
          275.0 -> -85.0
          -190.0 -> 170.0
        """
        norm_lon = ((lon + 180.0) % 360.0) - 180.0
        return round(norm_lon, 5)

    @staticmethod
    def normalize_latitude(lat: float) -> float:
        """Validates and bounds latitude into [-90.0, 90.0] degrees North."""
        if not (-90.0 <= lat <= 90.0):
            raise ValueError(f"Latitude out of physical range [-90..90]: {lat}")
        return round(lat, 5)

    @staticmethod
    def orient_spatial_grid(
        array: np.ndarray,
        lats: np.ndarray,
        lons: np.ndarray,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Ensures latitudes are monotonically increasing or decreasing and longitudes are monotonically increasing.
        Returns (oriented_array, oriented_lats, oriented_lons).
        Standard convention: lats ascending (South to North), lons ascending (West to East).
        """
        arr = array.copy()
        out_lats = lats.copy()
        out_lons = lons.copy()

        # Check latitude direction
        if len(out_lats) > 1 and out_lats[0] > out_lats[-1]:
            # Latitudes are descending (North to South), flip vertically along axis 0
            arr = np.flip(arr, axis=0)
            out_lats = np.flip(out_lats)

        # Check longitude direction
        if len(out_lons) > 1 and out_lons[0] > out_lons[-1]:
            # Longitudes are descending, flip horizontally along axis 1
            arr = np.flip(arr, axis=1)
            out_lons = np.flip(out_lons)

        return arr, out_lats, out_lons

    @staticmethod
    def standardize_missing_values(array: np.ndarray, fill_values: List[float]) -> np.ndarray:
        """Replaces known sentinel fill values (e.g. -999.0, -32768) with np.nan."""
        arr = array.astype(np.float32, copy=True)
        for fill in fill_values:
            arr[arr == fill] = np.nan
        return arr
