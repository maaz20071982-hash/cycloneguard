"""
Configuration for Satellite Data Acquisition in CycloneGuard.
Enforces safe boundaries, timeouts, retry limits, and environment-configurable paths.
"""

import os
from typing import Dict, Optional
from pydantic import BaseModel, Field


class AcquisitionConfig(BaseModel):
    """Configurable settings for automated and bounded data retrieval."""
    raw_data_dir: str = Field(default_factory=lambda: os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "raw")))
    samples_dir: str = Field(default_factory=lambda: os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "samples")))
    manifests_dir: str = Field(default_factory=lambda: os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "manifests")))
    processed_dir: str = Field(default_factory=lambda: os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "processed")))
    
    # Download safety bounds
    max_download_bytes: int = 100 * 1024 * 1024  # 100 MB hard limit per individual asset
    timeout_seconds: int = 30
    max_retries: int = 3
    backoff_factor: float = 1.5
    user_agent: str = "CycloneGuard-Research/1.0 (Meteorological Data Ingestion; contact@cycloneguard.org)"

    # Remote base URLs (configurable for local proxies or institutional mirrors)
    noaa_ncei_hursat_base: str = "https://www.ncei.noaa.gov/data/hurricane-satellite-hursat-b1/archive/v06/"
    noaa_ncei_ibtracs_base: str = "https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/"
    isro_mosdac_base: str = "https://www.mosdac.gov.in/api/v1/"
    eumetsat_datastore_base: str = "https://datastore.eumetsat.int/data/browse/"
    nasa_earthdata_base: str = "https://gpm1.gesdisc.eosdis.nasa.gov/data/"


def load_acquisition_config(env_prefix: str = "CYCLONEGUARD_") -> AcquisitionConfig:
    """Loads configuration with optional environment variable overrides."""
    kwargs = {}
    if os.getenv(f"{env_prefix}RAW_DATA_DIR"):
        kwargs["raw_data_dir"] = os.getenv(f"{env_prefix}RAW_DATA_DIR")
    if os.getenv(f"{env_prefix}MAX_DOWNLOAD_BYTES"):
        kwargs["max_download_bytes"] = int(os.getenv(f"{env_prefix}MAX_DOWNLOAD_BYTES"))
    if os.getenv(f"{env_prefix}TIMEOUT_SECONDS"):
        kwargs["timeout_seconds"] = int(os.getenv(f"{env_prefix}TIMEOUT_SECONDS"))
    return AcquisitionConfig(**kwargs)


default_config = load_acquisition_config()
