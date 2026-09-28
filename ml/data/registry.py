"""
CycloneGuard Central Data Source Registry.
Provides verified metadata, status, resolution, and access protocols for multi-source
meteorological observations and cyclone datasets.

Scientific Rules:
- No fabricated sources.
- No assumed connectivity without validation.
- Honest status classification.
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class DataSourceStatus(str, Enum):
    CONNECTED = "CONNECTED"
    AVAILABLE_FOR_DOWNLOAD = "AVAILABLE FOR DOWNLOAD"
    OPTIONAL = "OPTIONAL"
    UNAVAILABLE = "UNAVAILABLE"
    NOT_YET_INTEGRATED = "NOT YET INTEGRATED"


class DataSourceType(str, Enum):
    CYCLONE_TRACK = "cyclone_track"
    GEOSTATIONARY_INFRARED = "geostationary_infrared"
    GEOSTATIONARY_MULTISPECTRAL = "geostationary_multispectral"
    INTENSITY_OBJECTIVE = "intensity_objective"
    OCEAN_WIND_VECTOR = "ocean_wind_vector"
    PASSIVE_MICROWAVE = "passive_microwave"


class DataSourceDefinition(BaseModel):
    source_id: str
    name: str
    provider: str
    data_type: DataSourceType
    format: str
    temporal_resolution: Optional[str] = None
    spatial_resolution: Optional[str] = None
    coverage: Optional[str] = None
    status: DataSourceStatus
    download_method: Optional[str] = None
    documentation_url: Optional[str] = None
    records_processed: int = 0
    last_successful_update: Optional[str] = None
    last_failure: Optional[str] = None
    notes: Optional[str] = None


DATA_SOURCE_CATALOG: Dict[str, DataSourceDefinition] = {
    "noaa_ibtracs": DataSourceDefinition(
        source_id="noaa_ibtracs",
        name="NOAA IBTrACS (International Best Track Archive for Climate Stewardship)",
        provider="NOAA NCEI",
        data_type=DataSourceType.CYCLONE_TRACK,
        format="CSV / NetCDF-4",
        temporal_resolution="3-hourly / 6-hourly best-track records",
        spatial_resolution="0.1° center coordinate precision",
        coverage="North Indian Ocean (NI: Bay of Bengal & Arabian Sea) & Global",
        status=DataSourceStatus.AVAILABLE_FOR_DOWNLOAD,
        download_method="HTTPS direct CSV stream / NCEI open access",
        documentation_url="https://www.ncei.noaa.gov/products/international-best-track-archive",
        notes="Primary ground truth for cyclone track, central pressure, and 3-min/10-min sustained winds (including IMD New Delhi and JTWC reporting).",
    ),
    "noaa_hursat_b1": DataSourceDefinition(
        source_id="noaa_hursat_b1",
        name="NOAA HURSAT-B1 (Hurricane Satellite ISCCP B1 Gridded Imagery)",
        provider="NOAA NCEI",
        data_type=DataSourceType.GEOSTATIONARY_INFRARED,
        format="NetCDF-3 / NetCDF-4 (CF-compliant)",
        temporal_resolution="3-hourly storm-centered grids",
        spatial_resolution="~8 km (approx. 0.08° grid, ~301x301 pixels)",
        coverage="North Indian Ocean & Global Tropical Cyclones (1978–2015)",
        status=DataSourceStatus.AVAILABLE_FOR_DOWNLOAD,
        download_method="HTTPS / NCEI archive / NOAA Open Data Dissemination",
        documentation_url="https://www.ncei.noaa.gov/products/hurricane-satellite-data",
        notes="Calibrated Infrared Window (IRWIN ~11 µm), Water Vapor (IRWVP ~6.7 µm), and Visible (VSCHN) storm-centric satellite crops.",
    ),
    "noaa_adt_hursat": DataSourceDefinition(
        source_id="noaa_adt_hursat",
        name="NOAA ADT-HURSAT (Advanced Dvorak Technique - HURSAT Climate Record)",
        provider="NOAA NCEI / UW-CIMSS",
        data_type=DataSourceType.INTENSITY_OBJECTIVE,
        format="NetCDF-4",
        temporal_resolution="3-hourly",
        spatial_resolution="Storm-centric point & diagnostic eye/cloud temperatures",
        coverage="Global Tropical Cyclones (1978–2024)",
        status=DataSourceStatus.AVAILABLE_FOR_DOWNLOAD,
        download_method="NOAA Open Data Dissemination (NODD) S3 public bucket",
        documentation_url="https://www.ncei.noaa.gov/products/hurricane-satellite-data",
        notes="Objective satellite-derived intensity proxy (raw T-numbers, CI numbers, MSLP, Vmax). Must not be conflated with direct in-situ recon.",
    ),
    "isro_insat3d_mosdac": DataSourceDefinition(
        source_id="isro_insat3d_mosdac",
        name="ISRO INSAT-3D/3DR Meteorological Imager",
        provider="ISRO MOSDAC",
        data_type=DataSourceType.GEOSTATIONARY_MULTISPECTRAL,
        format="HDF5 / NetCDF",
        temporal_resolution="30-minute full disk / 15-minute rapid scan",
        spatial_resolution="1 km (VIS), 4 km (TIR1, TIR2, MIR), 8 km (WV)",
        coverage="Indian Ocean & South Asia (40°E–120°E, 45°S–45°N)",
        status=DataSourceStatus.NOT_YET_INTEGRATED,
        download_method="Authenticated REST API (requires individual MOSDAC credentials & session tokens)",
        documentation_url="https://www.mosdac.gov.in/",
        notes="Automated programmatic access requires verified user credentials; anonymous downloads not permitted. Latency: 3-day hold for L1 products without NRT authorization.",
    ),
    "eumetsat_ascat": DataSourceDefinition(
        source_id="eumetsat_ascat",
        name="EUMETSAT Metop ASCAT Ocean Surface Wind Vectors",
        provider="EUMETSAT / NOAA CoastWatch",
        data_type=DataSourceType.OCEAN_WIND_VECTOR,
        format="NetCDF-4 / BUFR",
        temporal_resolution="Orbital swaths (sub-daily coverage over storm path)",
        spatial_resolution="12.5 km / 25 km vector grid",
        coverage="Global ice-free oceans",
        status=DataSourceStatus.OPTIONAL,
        download_method="EUMETSAT Data Store API / NOAA CoastWatch ERDDAP",
        documentation_url="https://www.eumetsat.int/ascat",
        notes="C-band active scatterometer ocean wind vectors. Useful for gale radius (R34, R50) and low-level circulation center validation.",
    ),
    "gpm_gmi_microwave": DataSourceDefinition(
        source_id="gpm_gmi_microwave",
        name="NASA/JAXA GPM Microwave Imager (GMI) & Constellation",
        provider="NASA GES DISC / NOAA STAR",
        data_type=DataSourceType.PASSIVE_MICROWAVE,
        format="HDF5 / NetCDF-4",
        temporal_resolution="Non-uniform orbital overpasses (~1–2 per day per cyclone)",
        spatial_resolution="5 km to 25 km (10 GHz to 183 GHz channels)",
        coverage="Global tropical and subtropical oceans (65°S–65°N)",
        status=DataSourceStatus.OPTIONAL,
        download_method="NASA Earthdata authenticated HTTPS",
        documentation_url="https://gpm.nasa.gov/missions/GPM/GMI",
        notes="Passive microwave penetration through cloud canopy, revealing eyewall concentric rings and rainband structure.",
    ),
}


class DataSourceRegistry:
    """Registry manager for meteorological data sources."""

    def __init__(self, sources: Optional[Dict[str, DataSourceDefinition]] = None):
        self._sources = dict(sources or DATA_SOURCE_CATALOG)

    def get_source(self, source_id: str) -> Optional[DataSourceDefinition]:
        return self._sources.get(source_id)

    def list_sources(self) -> List[DataSourceDefinition]:
        return list(self._sources.values())

    def update_source_status(
        self,
        source_id: str,
        status: DataSourceStatus,
        records_processed: Optional[int] = None,
        last_successful_update: Optional[str] = None,
        last_failure: Optional[str] = None,
    ) -> Optional[DataSourceDefinition]:
        source = self._sources.get(source_id)
        if not source:
            return None
        source.status = status
        if records_processed is not None:
            source.records_processed = records_processed
        if last_successful_update is not None:
            source.last_successful_update = last_successful_update
        if last_failure is not None:
            source.last_failure = last_failure
        return source


# Global singleton instance
registry = DataSourceRegistry()
