"""
CycloneGuard Environmental Feature Engineering Engine.
Sprint 10 Deliverable.

Extracts physically and meteorologically interpretable large-scale environmental
features at cyclone-centered fix locations from verified reanalysis sources:
1. Deep-layer vertical wind shear (850 - 200 hPa vector difference) from ECMWF ERA5.
2. Mid-tropospheric relative humidity (700 hPa, 500 hPa) from ECMWF ERA5.
3. Sea surface temperature (SST) and thermodynamic potential from NOAA PSL OISST v2.0.

Rules:
- Strictly no fabricated values.
- Explicit availability flags for every variable family.
- Never zero-fill missing environmental values.
- Directional causality: only contemporaneous or historical observations (t <= t_0).
"""

from dataclasses import dataclass, field
import math
from typing import Any, Dict, List, Optional, Tuple
import numpy as np


# Canonical list of 13 environmental features (10 continuous + 3 boolean flags)
ENVIRONMENTAL_FEATURE_NAMES: Tuple[str, ...] = (
    # Group E1: Oceanic Thermal Potential
    "env_sst_celsius",
    "env_sst_potential_above_26c",
    "env_sst_is_observed",
    # Group E2: Deep-Layer Dynamical Wind Shear
    "env_vws_magnitude_kts",
    "env_vws_direction_deg",
    "env_wind_speed_850hpa_kts",
    "env_wind_speed_200hpa_kts",
    "env_vws_delta_6h_kts",
    "env_vws_is_observed",
    # Group E3: Mid-Tropospheric Moisture & Alignment
    "env_relative_humidity_700hpa",
    "env_relative_humidity_500hpa",
    "env_rh_is_observed",
    "env_dt_minutes",
)


@dataclass
class EnvironmentalObservation:
    """Raw physical values from reanalysis at cyclone center fix."""
    wind_speed_850hpa_kmh: Optional[float] = None
    wind_direction_850hpa_deg: Optional[float] = None
    wind_speed_200hpa_kmh: Optional[float] = None
    wind_direction_200hpa_deg: Optional[float] = None
    relative_humidity_700hpa_pct: Optional[float] = None
    relative_humidity_500hpa_pct: Optional[float] = None
    sst_celsius: Optional[float] = None
    dt_minutes: float = 0.0
    # Optional 6-hour antecedent observation for tendency
    prior_vws_magnitude_kts: Optional[float] = None


class EnvironmentalFeatureExtractor:
    """Extracts standardized environmental features from raw reanalysis observations."""

    KMH_TO_KNOTS = 1.0 / 1.852

    @classmethod
    def calculate_shear(
        cls,
        w850_kmh: Optional[float],
        d850_deg: Optional[float],
        w200_kmh: Optional[float],
        d200_deg: Optional[float],
    ) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
        """
        Calculates 850-200 hPa vertical wind shear vector.
        
        Returns:
            vws_magnitude_kts: Vector difference magnitude in knots.
            vws_direction_deg: Direction shear vector is pointing towards (degrees 0-360).
            w850_kts: 850 hPa wind speed in knots.
            w200_kts: 200 hPa wind speed in knots.
        """
        if None in (w850_kmh, d850_deg, w200_kmh, d200_deg):
            return None, None, None, None

        # Convert meteorological direction (wind blowing FROM) to vector components
        rad850 = math.radians(d850_deg)
        u850 = -w850_kmh * math.sin(rad850)
        v850 = -w850_kmh * math.cos(rad850)

        rad200 = math.radians(d200_deg)
        u200 = -w200_kmh * math.sin(rad200)
        v200 = -w200_kmh * math.cos(rad200)

        du = u200 - u850
        dv = v200 - v850

        mag_kmh = math.sqrt(du * du + dv * dv)
        mag_kts = mag_kmh * cls.KMH_TO_KNOTS

        # Direction of shear vector
        dir_deg = (math.degrees(math.atan2(-du, -dv)) + 360.0) % 360.0

        w850_kts = w850_kmh * cls.KMH_TO_KNOTS
        w200_kts = w200_kmh * cls.KMH_TO_KNOTS

        return float(mag_kts), float(dir_deg), float(w850_kts), float(w200_kts)

    @classmethod
    def extract_features(cls, obs: EnvironmentalObservation) -> Dict[str, float]:
        """
        Transforms raw observation into the canonical 13-feature environmental dictionary.
        """
        vws_mag, vws_dir, w850_kts, w200_kts = cls.calculate_shear(
            obs.wind_speed_850hpa_kmh,
            obs.wind_direction_850hpa_deg,
            obs.wind_speed_200hpa_kmh,
            obs.wind_direction_200hpa_deg,
        )

        # 6-hour shear delta
        delta_vws_6h: Optional[float] = None
        if vws_mag is not None and obs.prior_vws_magnitude_kts is not None:
            delta_vws_6h = float(vws_mag - obs.prior_vws_magnitude_kts)

        # SST potential (excess above 26.0°C threshold)
        sst = obs.sst_celsius
        sst_potential: Optional[float] = None
        if sst is not None and not np.isnan(sst) and sst > 0.0:
            sst_potential = float(max(0.0, sst - 26.0))
        else:
            sst = np.nan

        # Availability flags
        vws_avail = 1.0 if vws_mag is not None else 0.0
        sst_avail = 1.0 if (sst is not None and not np.isnan(sst) and sst > 0.0) else 0.0
        rh_avail = 1.0 if (obs.relative_humidity_700hpa_pct is not None and not np.isnan(obs.relative_humidity_700hpa_pct)) else 0.0

        return {
            "env_sst_celsius": float(sst) if sst_avail == 1.0 else np.nan,
            "env_sst_potential_above_26c": float(sst_potential) if sst_avail == 1.0 else np.nan,
            "env_sst_is_observed": sst_avail,
            "env_vws_magnitude_kts": float(vws_mag) if vws_avail == 1.0 else np.nan,
            "env_vws_direction_deg": float(vws_dir) if vws_avail == 1.0 else np.nan,
            "env_wind_speed_850hpa_kts": float(w850_kts) if vws_avail == 1.0 else np.nan,
            "env_wind_speed_200hpa_kts": float(w200_kts) if vws_avail == 1.0 else np.nan,
            "env_vws_delta_6h_kts": float(delta_vws_6h) if delta_vws_6h is not None else np.nan,
            "env_vws_is_observed": vws_avail,
            "env_relative_humidity_700hpa": float(obs.relative_humidity_700hpa_pct) if rh_avail == 1.0 else np.nan,
            "env_relative_humidity_500hpa": float(obs.relative_humidity_500hpa_pct) if (obs.relative_humidity_500hpa_pct is not None and not np.isnan(obs.relative_humidity_500hpa_pct)) else np.nan,
            "env_rh_is_observed": rh_avail,
            "env_dt_minutes": float(obs.dt_minutes),
        }
