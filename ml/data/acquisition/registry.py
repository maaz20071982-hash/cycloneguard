"""
CycloneGuard Satellite Data Source Inventory & Registry.
Sprint 7 - Phase 1 Deliverable.

Strict Scientific Rules:
1. Never claim a source is integrated merely because documentation exists.
2. Distinguish:
   - DOCUMENTED
   - AVAILABLE ONLINE
   - LOCALLY AVAILABLE
   - DOWNLOADED
   - PARSED
   - ALIGNED
   - TRAINING READY
3. No fabricated sources or synthetic coverage.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DataReadinessLevel(str, Enum):
    """Rigorous 7-stage readiness hierarchy for scientific observational datasets."""
    DOCUMENTED = "DOCUMENTED"
    AVAILABLE_ONLINE = "AVAILABLE ONLINE"
    LOCALLY_AVAILABLE = "LOCALLY AVAILABLE"
    DOWNLOADED = "DOWNLOADED"
    PARSED = "PARSED"
    ALIGNED = "ALIGNED"
    TRAINING_READY = "TRAINING READY"


class SatelliteSensorType(str, Enum):
    GEOSTATIONARY_INFRARED = "geostationary_infrared"
    GEOSTATIONARY_MULTISPECTRAL = "geostationary_multispectral"
    INTENSITY_OBJECTIVE = "intensity_objective"
    OCEAN_WIND_SCATTEROMETER = "ocean_wind_scatterometer"
    PASSIVE_MICROWAVE = "passive_microwave"
    BEST_TRACK = "best_track"


class SatelliteSourceMetadata(BaseModel):
    """Complete specification for a candidate or integrated meteorological source."""
    source_id: str
    source_name: str
    provider: str
    product: str
    sensor: str
    sensor_type: SatelliteSensorType
    channels: List[str]
    spatial_resolution: str
    temporal_resolution: str
    geographic_coverage: str
    available_years: str
    file_format: str
    access_method: str
    license_restrictions: str
    automated_retrieval_possible: bool
    current_local_availability: str
    current_integration_status: DataReadinessLevel
    local_files_count: int = 0
    total_observations_local: int = 0
    documentation_url: Optional[str] = None
    notes: Optional[str] = None


# Comprehensive Phase 1 Inventory
SATELLITE_SOURCE_CATALOG: Dict[str, SatelliteSourceMetadata] = {
    "noaa_hursat_b1": SatelliteSourceMetadata(
        source_id="noaa_hursat_b1",
        source_name="NOAA HURSAT-B1 (Hurricane Satellite ISCCP B1)",
        provider="NOAA National Centers for Environmental Information (NCEI)",
        product="HURSAT-B1 v06",
        sensor="ISCCP-B1 Geostationary Satellite Constellation (GOES, Meteosat, GMS, MTSAT, INSAT)",
        sensor_type=SatelliteSensorType.GEOSTATIONARY_INFRARED,
        channels=["IRWIN (10.8 µm)", "IRWVP (6.7 µm)", "VSCHN (0.6 µm)"],
        spatial_resolution="~8 km (approx. 0.08° grid, 301x301 pixels)",
        temporal_resolution="3-hourly storm-centered grids",
        geographic_coverage="Global Tropical Cyclone Basins (North Indian Ocean, Western Pacific, Atlantic, etc.)",
        available_years="1978–2016",
        file_format="NetCDF-3 Classic (CF-1.4 compliant)",
        access_method="HTTPS direct archive (https://www.ncei.noaa.gov/data/hurricane-satellite-hursat-b1/archive/v06/)",
        license_restrictions="Public Domain (US Government open access, no authentication required)",
        automated_retrieval_possible=True,
        current_local_availability="Locally available (data/samples/hursat_b1_sample_mocha.nc)",
        current_integration_status=DataReadinessLevel.ALIGNED,
        local_files_count=1,
        total_observations_local=1,
        documentation_url="https://www.ncei.noaa.gov/products/hurricane-satellite-data",
        notes="Primary infrared satellite archive with calibrated brightness temperatures. Sample file aligned with Cyclone Mocha.",
    ),
    "noaa_adt_hursat": SatelliteSourceMetadata(
        source_id="noaa_adt_hursat",
        source_name="NOAA ADT-HURSAT (Advanced Dvorak Technique - HURSAT Climate Record)",
        provider="NOAA NCEI / University of Wisconsin-Madison CIMSS",
        product="ADT-HURSAT v01r00",
        sensor="Geostationary infrared imagers (GOES, Meteosat, MTSAT, Himawari)",
        sensor_type=SatelliteSensorType.INTENSITY_OBJECTIVE,
        channels=["Raw T-number", "Final T-number", "Current Intensity (CI)", "Estimated MSLP (hPa)", "Estimated Vmax (kts)", "Eye Temp (°C)", "Cloud Temp (°C)"],
        spatial_resolution="Storm-centered diagnostic point extraction",
        temporal_resolution="3-hourly",
        geographic_coverage="Global Tropical Cyclones",
        available_years="1978–2024",
        file_format="NetCDF-4",
        access_method="NOAA Open Data Dissemination (NODD) S3 public bucket / NCEI archive",
        license_restrictions="Public Domain (Open access)",
        automated_retrieval_possible=True,
        current_local_availability="None currently staged locally",
        current_integration_status=DataReadinessLevel.AVAILABLE_ONLINE,
        local_files_count=0,
        total_observations_local=0,
        documentation_url="https://www.ncei.noaa.gov/products/hurricane-satellite-data",
        notes="Objective satellite intensity proxy. Must not be conflated with direct in-situ recon or agency best-track ground truth.",
    ),
    "isro_insat3d_mosdac": SatelliteSourceMetadata(
        source_id="isro_insat3d_mosdac",
        source_name="ISRO INSAT-3D / INSAT-3DR Imager",
        provider="ISRO Space Applications Centre (MOSDAC)",
        product="Level-1B Calibrated Radiance / Level-2 Geophysical Products",
        sensor="6-channel Imager (VIS, SWIR, MIR, TIR-1, TIR-2, WV)",
        sensor_type=SatelliteSensorType.GEOSTATIONARY_MULTISPECTRAL,
        channels=["TIR-1 (10.8 µm)", "TIR-2 (12.0 µm)", "MIR (3.9 µm)", "WV (6.8 µm)", "VIS (0.65 µm)"],
        spatial_resolution="1 km (VIS), 4 km (TIR1, TIR2, MIR), 8 km (WV)",
        temporal_resolution="30-min full disk (staggered 3D + 3DR for 15-min effective)",
        geographic_coverage="Indian Ocean and South Asia (40°E–120°E, 45°S–45°N)",
        available_years="2013–present (INSAT-3D: 2013–present, 3DR: 2016–present, 3DS: 2024–present)",
        file_format="HDF5",
        access_method="Authenticated REST API via MOSDAC user portal",
        license_restrictions="User registration required; non-commercial research; 3-day data latency for standard accounts",
        automated_retrieval_possible=False,
        current_local_availability="None staged locally (pending individual user credential provisioning)",
        current_integration_status=DataReadinessLevel.DOCUMENTED,
        local_files_count=0,
        total_observations_local=0,
        documentation_url="https://www.mosdac.gov.in/",
        notes="Critical regional coverage for Bay of Bengal and Arabian Sea. Automated bulk retrieval blocked without user token.",
    ),
    "eumetsat_ascat": SatelliteSourceMetadata(
        source_id="eumetsat_ascat",
        source_name="EUMETSAT Metop ASCAT Ocean Surface Wind Vectors",
        provider="EUMETSAT / KNMI / NOAA CoastWatch",
        product="ASCAT Coastal Ocean Surface Winds",
        sensor="Advanced Scatterometer (C-band 5.255 GHz real aperture radar)",
        sensor_type=SatelliteSensorType.OCEAN_WIND_SCATTEROMETER,
        channels=["10m neutral equivalent wind speed (m/s)", "wind direction (° clockwise from N)", "backscatter", "rain flags"],
        spatial_resolution="12.5 km / 25 km vector grid along swath",
        temporal_resolution="Orbital swaths (~1–2 overpasses daily per storm location)",
        geographic_coverage="Global ice-free oceans",
        available_years="2006–present (Metop-A: 2006–2021, Metop-B: 2012–present, Metop-C: 2018–present)",
        file_format="NetCDF-4 / BUFR",
        access_method="EUMETSAT Data Store API / NOAA CoastWatch ERDDAP open server",
        license_restrictions="Open access (CC-BY or free research registration)",
        automated_retrieval_possible=True,
        current_local_availability="None currently staged locally",
        current_integration_status=DataReadinessLevel.AVAILABLE_ONLINE,
        local_files_count=0,
        total_observations_local=0,
        documentation_url="https://www.eumetsat.int/ascat",
        notes="Auxiliary validation for circulation center and gale radii (R34, R50). Swaths are non-uniform in time.",
    ),
    "gpm_gmi_microwave": SatelliteSourceMetadata(
        source_id="gpm_gmi_microwave",
        source_name="NASA/JAXA GPM Microwave Imager (GMI) & Constellation",
        provider="NASA GES DISC / JAXA",
        product="GPM Level-1B Calibrated Brightness Temperatures",
        sensor="GPM Microwave Imager (GMI), SSMIS, AMSR2",
        sensor_type=SatelliteSensorType.PASSIVE_MICROWAVE,
        channels=["Tc_10.65GHz", "Tc_18.7GHz", "Tc_36.5GHz", "Tc_89.0GHz", "Tc_166.0GHz", "Tc_183.3GHz"],
        spatial_resolution="5 km (89 GHz) to 25 km (10 GHz) footprint",
        temporal_resolution="Orbital overpasses (intermittent, ~1–2 overpasses per 24h period)",
        geographic_coverage="Global tropical and subtropical oceans (65°S–65°N)",
        available_years="2014–present (TRMM: 1997–2015, GPM: 2014–present)",
        file_format="HDF5 / NetCDF-4",
        access_method="NASA Earthdata HTTPS (requires Earthdata Login in .netrc)",
        license_restrictions="Open access with free NASA Earthdata account",
        automated_retrieval_possible=True,
        current_local_availability="None currently staged locally",
        current_integration_status=DataReadinessLevel.AVAILABLE_ONLINE,
        local_files_count=0,
        total_observations_local=0,
        documentation_url="https://gpm.nasa.gov/missions/GPM/GMI",
        notes="High-frequency microwave penetrates cloud canopy to resolve eyewall convection and concentric eyewall cycles.",
    ),
    "noaa_ibtracs": SatelliteSourceMetadata(
        source_id="noaa_ibtracs",
        source_name="NOAA IBTrACS (International Best Track Archive for Climate Stewardship)",
        provider="NOAA NCEI / WMO Tropical Cyclone Programme",
        product="IBTrACS v04r01 Best Track",
        sensor="Multi-agency synoptic best-track consensus (IMD RSMC New Delhi, JTWC, CMA, JMA)",
        sensor_type=SatelliteSensorType.BEST_TRACK,
        channels=["Latitude", "Longitude", "Max Sustained Wind (kts)", "Min Central Pressure (mb)", "Translation Speed", "Translation Direction"],
        spatial_resolution="0.1° center coordinates",
        temporal_resolution="3-hourly / 6-hourly synoptic fixes",
        geographic_coverage="North Indian Ocean (NI) & Global",
        available_years="1842–present",
        file_format="CSV / NetCDF-4",
        access_method="Direct open HTTPS download from NOAA NCEI",
        license_restrictions="Public Domain (US Government open access)",
        automated_retrieval_possible=True,
        current_local_availability="Locally available (data/samples/ibtracs_sample_ni.csv)",
        current_integration_status=DataReadinessLevel.TRAINING_READY,
        local_files_count=1,
        total_observations_local=400,
        documentation_url="https://www.ncei.noaa.gov/products/international-best-track-archive",
        notes="Primary ground truth for cyclone track kinematics, intensity, and 24h RI label derivation.",
    ),
}


class SatelliteSourceRegistry:
    """Manager for querying and updating the satellite source registry."""

    def __init__(self, sources: Optional[Dict[str, SatelliteSourceMetadata]] = None):
        self._sources = dict(sources or SATELLITE_SOURCE_CATALOG)

    def get_source(self, source_id: str) -> Optional[SatelliteSourceMetadata]:
        return self._sources.get(source_id)

    def list_sources(self) -> List[SatelliteSourceMetadata]:
        return list(self._sources.values())

    def get_sources_by_readiness(self, level: DataReadinessLevel) -> List[SatelliteSourceMetadata]:
        return [s for s in self._sources.values() if s.current_integration_status == level]

    def update_readiness(
        self,
        source_id: str,
        level: DataReadinessLevel,
        local_files_count: Optional[int] = None,
        total_observations_local: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> Optional[SatelliteSourceMetadata]:
        src = self._sources.get(source_id)
        if not src:
            return None
        src.current_integration_status = level
        if local_files_count is not None:
            src.local_files_count = local_files_count
        if total_observations_local is not None:
            src.total_observations_local = total_observations_local
        if notes:
            src.notes = notes
        return src


# Global singleton
source_registry = SatelliteSourceRegistry()
