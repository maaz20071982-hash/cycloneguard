"""
NOAA IBTrACS Source Adapter for CycloneGuard.
Ingests, parses, validates, and normalizes best-track tropical cyclone records
with specialized support for North Indian Ocean (Bay of Bengal & Arabian Sea) storms,
including IMD (RSMC New Delhi) official classification and pressure/wind reporting.
"""

from datetime import datetime
import os
from typing import Any, Dict, List, Optional
import urllib.request

from ml.data.adapters.base import BaseDataSourceAdapter
from ml.data.schemas.adapter_results import (
    DiscoveredResource,
    DownloadResult,
    DownloadStatus,
    NormalizedData,
    ParsedData,
    ValidationCheck,
    ValidationReport,
    ValidationSeverity,
)
from ml.data.schemas.track import CycloneTrackPoint, CycloneTrackSeries

NOAA_NCEI_CSV_BASE = "https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/"


class IBTrACSAdapter(BaseDataSourceAdapter):
    """Adapter for NOAA IBTrACS v04r01 Best Track Archive."""

    def __init__(self):
        super().__init__("noaa_ibtracs")

    def discover(self, filters: Optional[Dict[str, Any]] = None) -> List[DiscoveredResource]:
        """Discovers standard verified IBTrACS dataset files available from NOAA NCEI."""
        resources = [
            DiscoveredResource(
                resource_id="ibtracs_ni_v04r01",
                source_id=self.source_id,
                name="IBTrACS North Indian Ocean (NI) Basin Subset v04r01",
                remote_url=f"{NOAA_NCEI_CSV_BASE}ibtracs.NI.list.v04r01.csv",
                time_coverage="1842-present",
                spatial_coverage="North Indian Ocean (Bay of Bengal & Arabian Sea)",
                format="CSV",
                metadata={"basin": "NI", "version": "v04r01"},
            ),
            DiscoveredResource(
                resource_id="ibtracs_last3years_v04r01",
                source_id=self.source_id,
                name="IBTrACS Recent Cyclones (Last 3 Years) v04r01",
                remote_url=f"{NOAA_NCEI_CSV_BASE}ibtracs.last3years.list.v04r01.csv",
                time_coverage="Last 3 calendar years (Rolling update)",
                spatial_coverage="Global (All basins)",
                format="CSV",
                metadata={"scope": "recent", "version": "v04r01"},
            ),
            DiscoveredResource(
                resource_id="ibtracs_active_v04r01",
                source_id=self.source_id,
                name="IBTrACS Currently Active Storms v04r01",
                remote_url=f"{NOAA_NCEI_CSV_BASE}ibtracs.ACTIVE.list.v04r01.csv",
                time_coverage="Current real-time / active systems",
                spatial_coverage="Global",
                format="CSV",
                metadata={"scope": "active", "version": "v04r01"},
            ),
        ]
        if filters and "basin" in filters:
            basin_filter = filters["basin"]
            resources = [r for r in resources if r.metadata.get("basin") == basin_filter or r.metadata.get("scope") == "recent"]
        return resources

    def download(self, resource_id: str, target_dir: str) -> DownloadResult:
        """Downloads selected IBTrACS CSV resource to local storage."""
        available = {r.resource_id: r for r in self.discover()}
        if resource_id not in available:
            return DownloadResult(
                source_id=self.source_id,
                resource_id=resource_id,
                status=DownloadStatus.FAILED,
                message=f"Resource '{resource_id}' not found in discovery list.",
            )

        resource = available[resource_id]
        if not resource.remote_url:
            return DownloadResult(
                source_id=self.source_id,
                resource_id=resource_id,
                status=DownloadStatus.FAILED,
                message="Resource has no remote URL.",
            )

        os.makedirs(target_dir, exist_ok=True)
        filename = os.path.basename(resource.remote_url)
        target_file = os.path.join(target_dir, filename)

        try:
            req = urllib.request.Request(resource.remote_url, headers={"User-Agent": "CycloneGuard/1.0"})
            with urllib.request.urlopen(req, timeout=60) as resp, open(target_file, "wb") as f:
                for chunk in iter(lambda: resp.read(65536), b""):
                    f.write(chunk)

            size = os.path.getsize(target_file)
            sha256 = self.compute_sha256(target_file)
            return DownloadResult(
                source_id=self.source_id,
                resource_id=resource_id,
                status=DownloadStatus.COMPLETED,
                local_path=target_file,
                file_size_bytes=size,
                checksum_sha256=sha256,
                message="Downloaded IBTrACS dataset successfully.",
            )
        except Exception as e:
            return DownloadResult(
                source_id=self.source_id,
                resource_id=resource_id,
                status=DownloadStatus.FAILED,
                message=f"Download failed: {str(e)}",
            )

    def validate(self, file_path: str) -> ValidationReport:
        """Validates CSV format, columns, geographic bounds, and timestamps."""
        report = ValidationReport(source_id=self.source_id, file_path=file_path, status=ValidationSeverity.VALID)

        if not os.path.exists(file_path):
            report.status = ValidationSeverity.ERROR
            report.checks.append(ValidationCheck(
                check_name="file_exists",
                passed=False,
                severity=ValidationSeverity.ERROR,
                message=f"File not found: {file_path}",
            ))
            report.summary = "Validation failed: file not found."
            return report

        report.checks.append(ValidationCheck(
            check_name="file_exists",
            passed=True,
            severity=ValidationSeverity.VALID,
            message="File exists.",
        ))

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                header_line = f.readline().strip()
                units_line = f.readline().strip()

                columns = [c.strip() for c in header_line.split(",")]
                required_cols = ["SID", "SEASON", "BASIN", "NAME", "ISO_TIME", "LAT", "LON"]
                missing_cols = [rc for rc in required_cols if rc not in columns]

                if missing_cols:
                    report.status = ValidationSeverity.ERROR
                    report.checks.append(ValidationCheck(
                        check_name="header_columns",
                        passed=False,
                        severity=ValidationSeverity.ERROR,
                        message=f"Missing essential IBTrACS columns: {missing_cols}",
                    ))
                    report.summary = "Validation failed: required columns missing."
                    return report

                report.checks.append(ValidationCheck(
                    check_name="header_columns",
                    passed=True,
                    severity=ValidationSeverity.VALID,
                    message=f"Found {len(columns)} columns including all required headers.",
                    details={"total_columns": len(columns)},
                ))

                lat_idx = columns.index("LAT")
                lon_idx = columns.index("LON")
                time_idx = columns.index("ISO_TIME")
                sid_idx = columns.index("SID")

                invalid_coords = 0
                invalid_dates = 0
                row_count = 0
                storms_seen = set()

                for line in f:
                    row_count += 1
                    parts = [p.strip() for p in line.split(",")]
                    if len(parts) <= max(lat_idx, lon_idx, time_idx, sid_idx):
                        continue

                    sid = parts[sid_idx]
                    storms_seen.add(sid)

                    # Validate coordinates
                    try:
                        lat = float(parts[lat_idx])
                        lon = float(parts[lon_idx])
                        if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 360.0):
                            invalid_coords += 1
                    except ValueError:
                        invalid_coords += 1

                    # Validate timestamp
                    t_str = parts[time_idx]
                    try:
                        datetime.fromisoformat(t_str)
                    except ValueError:
                        invalid_dates += 1

            if invalid_coords > 0:
                report.checks.append(ValidationCheck(
                    check_name="coordinate_validity",
                    passed=False,
                    severity=ValidationSeverity.WARNING,
                    message=f"Found {invalid_coords} rows with unparseable or out-of-range coordinates.",
                ))
            else:
                report.checks.append(ValidationCheck(
                    check_name="coordinate_validity",
                    passed=True,
                    severity=ValidationSeverity.VALID,
                    message="All checked coordinate fields are within valid numeric bounds.",
                ))

            if invalid_dates > 0:
                report.checks.append(ValidationCheck(
                    check_name="timestamp_validity",
                    passed=False,
                    severity=ValidationSeverity.WARNING,
                    message=f"Found {invalid_dates} rows with invalid ISO timestamp strings.",
                ))
            else:
                report.checks.append(ValidationCheck(
                    check_name="timestamp_validity",
                    passed=True,
                    severity=ValidationSeverity.VALID,
                    message="All checked timestamps are valid ISO dates.",
                ))

            report.summary = f"Validated {row_count} records across {len(storms_seen)} cyclones."
            report.status = ValidationSeverity.WARNING if (invalid_coords > 0 or invalid_dates > 0) else ValidationSeverity.VALID

        except Exception as e:
            report.status = ValidationSeverity.ERROR
            report.checks.append(ValidationCheck(
                check_name="file_read",
                passed=False,
                severity=ValidationSeverity.ERROR,
                message=f"Error reading IBTrACS CSV: {str(e)}",
            ))
            report.summary = f"File read error: {str(e)}"

        return report

    def parse(self, file_path: str) -> ParsedData:
        """Parses CSV rows into structured raw dictionary records."""
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            header_line = f.readline().strip()
            units_line = f.readline().strip()
            headers = [c.strip() for c in header_line.split(",")]
            units = [u.strip() for u in units_line.split(",")]

            records = []
            for line in f:
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= len(headers):
                    row_dict = {headers[i]: parts[i] for i in range(len(headers))}
                    records.append(row_dict)

        return ParsedData(
            source_id=self.source_id,
            file_path=file_path,
            records_count=len(records),
            raw_variables=headers,
            raw_dimensions={"records": len(records), "variables": len(headers)},
            raw_attributes={"units_header": units_line},
            data_payload=records,
        )

    def normalize(self, parsed_data: ParsedData) -> NormalizedData:
        """Converts parsed records into standardized CycloneTrackPoint series grouped by storm."""
        raw_rows = parsed_data.data_payload or []
        series_by_storm: Dict[str, CycloneTrackSeries] = {}
        log = []

        total_points = 0
        for row in raw_rows:
            sid = row.get("SID", "").strip()
            if not sid:
                continue

            name = row.get("NAME", "UNNAMED").strip()
            if name in ("", "NOT_NAMED", "UNNAMED"):
                name = "UNNAMED"

            season_str = row.get("SEASON", "0").strip()
            try:
                season = int(season_str)
            except ValueError:
                season = 0

            basin = row.get("BASIN", "").strip()
            subbasin = row.get("SUBBASIN", "").strip() or None

            time_str = row.get("ISO_TIME", "").strip()
            try:
                dt = datetime.fromisoformat(time_str)
                iso_utc = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                continue

            try:
                lat = float(row.get("LAT", "0"))
                lon = float(row.get("LON", "0"))
                # Normalize longitude to [-180, 180]
                if lon > 180.0:
                    lon -= 360.0
            except ValueError:
                continue

            # Standard wind & pressure (WMO)
            wmo_wind = self._parse_float(row.get("WMO_WIND"))
            wmo_pres = self._parse_float(row.get("WMO_PRES"))

            # Regional agency wind & pressure (IMD New Delhi for North Indian Ocean)
            imd_wind = self._parse_float(row.get("NEWDELHI_WIND"))
            imd_pres = self._parse_float(row.get("NEWDELHI_PRES"))
            imd_grade = row.get("NEWDELHI_GRADE", "").strip() or None

            # Fallback to USA agency if WMO is missing
            if wmo_wind is None:
                wmo_wind = self._parse_float(row.get("USA_WIND"))
            if wmo_pres is None:
                wmo_pres = self._parse_float(row.get("USA_PRES"))

            dist2land = self._parse_float(row.get("DIST2LAND"))
            landfall_val = row.get("LANDFALL", "").strip()
            landfall = (landfall_val == "0") if landfall_val else None

            point = CycloneTrackPoint(
                storm_id=sid,
                storm_name=name,
                season=season,
                basin=basin,
                subbasin=subbasin,
                timestamp_utc=iso_utc,
                latitude=round(lat, 3),
                longitude=round(lon, 3),
                nature=row.get("NATURE", "").strip() or None,
                wind_speed_kts=wmo_wind,
                central_pressure_mb=wmo_pres,
                agency_wind_kts=imd_wind,
                agency_pressure_mb=imd_pres,
                agency_grade=imd_grade,
                dist2land_km=dist2land,
                landfall=landfall,
                raw_source="ibtracs",
            )

            if sid not in series_by_storm:
                series_by_storm[sid] = CycloneTrackSeries(
                    storm_id=sid,
                    storm_name=name,
                    season=season,
                    basin=basin,
                    points=[],
                )
            series_by_storm[sid].points.append(point)
            total_points += 1

        # Sort each storm series chronologically
        for series in series_by_storm.values():
            series.points.sort(key=lambda p: p.timestamp_utc)

        log.append(f"Normalized {total_points} observation points across {len(series_by_storm)} storm tracks.")

        # Compute bounding box
        all_lats = [p.latitude for s in series_by_storm.values() for p in s.points]
        all_lons = [p.longitude for s in series_by_storm.values() for p in s.points]
        spatial_bounds = {
            "lat_min": min(all_lats) if all_lats else 0.0,
            "lat_max": max(all_lats) if all_lats else 0.0,
            "lon_min": min(all_lons) if all_lons else 0.0,
            "lon_max": max(all_lons) if all_lons else 0.0,
        }

        all_times = [p.timestamp_utc for s in series_by_storm.values() for p in s.points]
        time_range = (min(all_times), max(all_times)) if all_times else None

        return NormalizedData(
            source_id=self.source_id,
            normalized_type="cyclone_track_series",
            records_count=total_points,
            time_range_utc=time_range,
            spatial_bounds=spatial_bounds,
            data_payload=series_by_storm,
            units={
                "latitude": "degrees_north [-90..90]",
                "longitude": "degrees_east [-180..180]",
                "wind_speed_kts": "knots (1-minute or 10-minute maximum sustained)",
                "agency_wind_kts": "knots (3-minute maximum sustained for IMD)",
                "central_pressure_mb": "millibars / hPa",
                "agency_pressure_mb": "millibars / hPa",
                "timestamp_utc": "ISO 8601 UTC (YYYY-MM-DDTHH:MM:SSZ)",
            },
            normalization_log=log,
        )

    @staticmethod
    def _parse_float(val: Optional[str]) -> Optional[float]:
        if not val:
            return None
        v = val.strip()
        if not v or v in ("-999", "-999.0", "NA", "NaN", "null"):
            return None
        try:
            return float(v)
        except ValueError:
            return None
