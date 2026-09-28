"""
Temporal & Multi-Source Coincidence Engine for CycloneGuard.
Sprint 7 - Phase 4 & Phase 7 Deliverables.

Scientific Principles:
1. Every IBTrACS cyclone observation fix is matched against registered satellite assets.
2. Temporal matching uses explicit, scientifically justified tolerances.
3. Exact delta_minutes is ALWAYS recorded (cyclone_time vs satellite_time).
4. No observations hours apart are silently treated as simultaneous.
5. No missing sensor is ever fabricated or assumed present.
"""

from datetime import datetime, timezone
import math
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from ml.data.manifests.satellite_manifest import SatelliteAssetManifestRecord
from ml.data.schemas.track import CycloneTrackPoint, CycloneTrackSeries


class TemporalCoincidenceToleranceConfig(BaseModel):
    """
    Configurable temporal matching tolerances with documented scientific rationales.
    """
    geostationary_minutes: float = 30.0
    polar_orbiting_minutes: float = 90.0
    microwave_minutes: float = 120.0
    scatterometer_minutes: float = 120.0

    rationales: Dict[str, str] = Field(
        default_factory=lambda: {
            "geostationary": (
                "±30 minutes. Geostationary instruments scan every 15-30 min. "
                "Convective core evolution occurs on ~30-min timescales (Kaplan et al. 2010); "
                "pairing beyond 30 min risks associating decoupled convective morphology with track state."
            ),
            "polar_orbiting": (
                "±90 minutes. Sun-synchronous low-Earth orbit period is ~100 min. "
                "A ±90 min window captures the single closest polar overpass without cross-orbit ambiguity."
            ),
            "microwave": (
                "±120 minutes. Polar microwave radiometers have sparse temporal coverage (~1-2 overpasses daily). "
                "A ±2-hour window captures internal eyewall precipitation structures while recording exact latency."
            ),
            "scatterometer": (
                "±120 minutes. C-band scatterometers (ASCAT) capture synoptic wind fields that evolve on multi-hour timescales. "
                "A ±120 min window ensures valid gale radii association while documenting exact delta_minutes."
            ),
        }
    )

    def get_tolerance_for_source_type(self, source_type: str) -> float:
        st = source_type.lower()
        if "geostationary" in st or "infrared" in st or "hursat" in st or "insat" in st:
            return self.geostationary_minutes
        elif "microwave" in st or "gmi" in st:
            return self.microwave_minutes
        elif "scatterometer" in st or "ascat" in st:
            return self.scatterometer_minutes
        elif "polar" in st:
            return self.polar_orbiting_minutes
        return self.geostationary_minutes


class SourceMatchDetail(BaseModel):
    """Details of a single source match against a cyclone observation."""
    available: bool = False
    asset_id: Optional[str] = None
    file_path: Optional[str] = None
    satellite_time_utc: Optional[str] = None
    delta_minutes: Optional[float] = None
    sensor: Optional[str] = None
    channel: Optional[str] = None
    is_within_tolerance: bool = False
    tolerance_used_minutes: float = 30.0
    spatial_coverage_status: str = "UNCHECKED"  # WITHIN_BOUNDS, OUT_OF_BOUNDS, UNCHECKED
    quality_status: str = "NOT_AVAILABLE"       # NOMINAL, DEGRADED, REJECTED, NOT_AVAILABLE
    quality_flags: List[str] = Field(default_factory=list)


class MultiSourceCoincidenceRow(BaseModel):
    """
    Central multimodal observation row uniting IBTrACS best-track with multi-source evidence.
    Bridge between raw satellite data, tracks, and future ML feature sets.
    """
    storm_id: str
    storm_name: str
    cyclone_time_utc: str
    latitude: float
    longitude: float
    wind_speed_kts: Optional[float] = None
    central_pressure_mb: Optional[float] = None
    nature: Optional[str] = None

    # Partition
    partition: str = "TRAIN"  # TRAIN, VAL, TEST

    # Multi-source channels
    ir_available: bool = False
    ir_asset_id: Optional[str] = None
    ir_file_path: Optional[str] = None
    ir_time_utc: Optional[str] = None
    ir_delta_minutes: Optional[float] = None
    ir_quality: str = "NOT_AVAILABLE"

    microwave_available: bool = False
    microwave_asset_id: Optional[str] = None
    microwave_file_path: Optional[str] = None
    microwave_time_utc: Optional[str] = None
    microwave_delta_minutes: Optional[float] = None
    microwave_quality: str = "NOT_AVAILABLE"

    scatterometer_available: bool = False
    scatterometer_asset_id: Optional[str] = None
    scatterometer_file_path: Optional[str] = None
    scatterometer_time_utc: Optional[str] = None
    scatterometer_delta_minutes: Optional[float] = None
    scatterometer_quality: str = "NOT_AVAILABLE"

    # Multimodal coincidence metrics
    total_coincident_sources: int = 0
    coincidence_quality: str = "TRACK_ONLY"  # TRACK_ONLY, UNIMODAL_IR, BIMODAL, TRIMODAL
    coincidence_flags: List[str] = Field(default_factory=list)


class CoincidenceEngine:
    """Matches cyclone track points with satellite assets in space and time."""

    def __init__(self, tolerances: Optional[TemporalCoincidenceToleranceConfig] = None):
        self.tolerances = tolerances or TemporalCoincidenceToleranceConfig()

    @staticmethod
    def parse_iso(ts_str: str) -> datetime:
        """Parses ISO 8601 string to timezone-aware UTC datetime."""
        clean = ts_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt

    def match_asset_to_track_point(
        self,
        point: CycloneTrackPoint,
        asset: SatelliteAssetManifestRecord,
    ) -> SourceMatchDetail:
        """Evaluates whether a satellite asset matches a track point in space and time."""
        track_dt = self.parse_iso(point.timestamp_utc)
        sat_dt = self.parse_iso(asset.timestamp)

        delta_sec = (sat_dt - track_dt).total_seconds()
        delta_min = round(delta_sec / 60.0, 2)

        tol_min = self.tolerances.get_tolerance_for_source_type(asset.source)
        is_within_tol = abs(delta_min) <= tol_min

        # Check spatial bounding box
        cov = asset.coverage
        lat_min = cov.get("lat_min", -90.0)
        lat_max = cov.get("lat_max", 90.0)
        lon_min = cov.get("lon_min", -180.0)
        lon_max = cov.get("lon_max", 180.0)

        within_spatial = (lat_min <= point.latitude <= lat_max) and (lon_min <= point.longitude <= lon_max)
        spatial_status = "WITHIN_BOUNDS" if within_spatial else "OUT_OF_BOUNDS"

        flags = list(asset.quality_flags)
        if not within_spatial:
            flags.append("CENTER_OUTSIDE_SATELLITE_COVERAGE")
        if not is_within_tol:
            flags.append(f"TIME_DELTA_EXCEEDS_TOLERANCE_{abs(delta_min):.1f}m_GT_{tol_min:.1f}m")

        # Determine quality
        if not within_spatial or not is_within_tol:
            q_status = "REJECTED"
        elif asset.status == "DEGRADED":
            q_status = "DEGRADED"
        elif asset.status == "REJECTED":
            q_status = "REJECTED"
        else:
            q_status = "NOMINAL"

        return SourceMatchDetail(
            available=is_within_tol and within_spatial and (asset.status != "REJECTED"),
            asset_id=asset.asset_id,
            file_path=asset.file_path,
            satellite_time_utc=asset.timestamp,
            delta_minutes=delta_min,
            sensor=asset.sensor,
            channel=asset.channel,
            is_within_tolerance=is_within_tol,
            tolerance_used_minutes=tol_min,
            spatial_coverage_status=spatial_status,
            quality_status=q_status,
            quality_flags=flags,
        )

    def build_multimodal_coincidence_table(
        self,
        track_points: List[CycloneTrackPoint],
        satellite_manifests: List[SatelliteAssetManifestRecord],
        partition_map: Optional[Dict[str, str]] = None,
    ) -> List[MultiSourceCoincidenceRow]:
        """
        Creates the complete MultiSourceCoincidenceRow table for all track points.
        Evaluates IR, microwave, and scatterometer availability honestly.
        """
        partition_map = partition_map or {}
        rows: List[MultiSourceCoincidenceRow] = []

        # Index manifests by storm_id for fast lookup
        manifests_by_storm: Dict[str, List[SatelliteAssetManifestRecord]] = {}
        for m in satellite_manifests:
            sid = m.storm_id or "UNKNOWN"
            if sid not in manifests_by_storm:
                manifests_by_storm[sid] = []
            manifests_by_storm[sid].append(m)

        for pt in track_points:
            storm_manifests = manifests_by_storm.get(pt.storm_id, [])
            storm_partition = partition_map.get(pt.storm_id, "TRAIN")

            # Match IR (HURSAT / INSAT)
            ir_match: Optional[SourceMatchDetail] = None
            best_ir_delta = float("inf")

            for m in storm_manifests:
                if "hursat" in m.source or "insat" in m.source or "infrared" in m.source:
                    detail = self.match_asset_to_track_point(pt, m)
                    if detail.available and abs(detail.delta_minutes or 0) < best_ir_delta:
                        best_ir_delta = abs(detail.delta_minutes or 0)
                        ir_match = detail

            # Match Microwave (GPM / SSMIS)
            mw_match: Optional[SourceMatchDetail] = None
            best_mw_delta = float("inf")
            for m in storm_manifests:
                if "microwave" in m.source or "gmi" in m.source:
                    detail = self.match_asset_to_track_point(pt, m)
                    if detail.available and abs(detail.delta_minutes or 0) < best_mw_delta:
                        best_mw_delta = abs(detail.delta_minutes or 0)
                        mw_match = detail

            # Match Scatterometer (ASCAT)
            scat_match: Optional[SourceMatchDetail] = None
            best_scat_delta = float("inf")
            for m in storm_manifests:
                if "scatterometer" in m.source or "ascat" in m.source:
                    detail = self.match_asset_to_track_point(pt, m)
                    if detail.available and abs(detail.delta_minutes or 0) < best_scat_delta:
                        best_scat_delta = abs(detail.delta_minutes or 0)
                        scat_match = detail

            # Count sources
            coincident_count = 0
            if ir_match and ir_match.available:
                coincident_count += 1
            if mw_match and mw_match.available:
                coincident_count += 1
            if scat_match and scat_match.available:
                coincident_count += 1

            if coincident_count == 0:
                coinc_quality = "TRACK_ONLY"
            elif coincident_count == 1:
                coinc_quality = "UNIMODAL_IR" if (ir_match and ir_match.available) else "UNIMODAL_OTHER"
            elif coincident_count == 2:
                coinc_quality = "BIMODAL"
            else:
                coinc_quality = "TRIMODAL_FULL"

            flags = []
            if coincident_count == 0:
                flags.append("NO_COINCIDENT_SATELLITE_DATA")
            if ir_match and ir_match.quality_flags:
                flags.extend([f"IR_{f}" for f in ir_match.quality_flags])

            row = MultiSourceCoincidenceRow(
                storm_id=pt.storm_id,
                storm_name=pt.storm_name,
                cyclone_time_utc=pt.timestamp_utc,
                latitude=pt.latitude,
                longitude=pt.longitude,
                wind_speed_kts=pt.wind_speed_kts,
                central_pressure_mb=pt.central_pressure_mb,
                nature=pt.nature,
                partition=storm_partition,
                # IR
                ir_available=(ir_match is not None and ir_match.available),
                ir_asset_id=ir_match.asset_id if ir_match else None,
                ir_file_path=ir_match.file_path if ir_match else None,
                ir_time_utc=ir_match.satellite_time_utc if ir_match else None,
                ir_delta_minutes=ir_match.delta_minutes if ir_match else None,
                ir_quality=ir_match.quality_status if ir_match else "NOT_AVAILABLE",
                # Microwave
                microwave_available=(mw_match is not None and mw_match.available),
                microwave_asset_id=mw_match.asset_id if mw_match else None,
                microwave_file_path=mw_match.file_path if mw_match else None,
                microwave_time_utc=mw_match.satellite_time_utc if mw_match else None,
                microwave_delta_minutes=mw_match.delta_minutes if mw_match else None,
                microwave_quality=mw_match.quality_status if mw_match else "NOT_AVAILABLE",
                # Scatterometer
                scatterometer_available=(scat_match is not None and scat_match.available),
                scatterometer_asset_id=scat_match.asset_id if scat_match else None,
                scatterometer_file_path=scat_match.file_path if scat_match else None,
                scatterometer_time_utc=scat_match.satellite_time_utc if scat_match else None,
                scatterometer_delta_minutes=scat_match.delta_minutes if scat_match else None,
                scatterometer_quality=scat_match.quality_status if scat_match else "NOT_AVAILABLE",
                # Multimodal summary
                total_coincident_sources=coincident_count,
                coincidence_quality=coinc_quality,
                coincidence_flags=flags,
            )
            rows.append(row)

        return rows
