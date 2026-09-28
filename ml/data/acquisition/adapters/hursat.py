"""
HURSAT-B1 Acquisition Adapter for NOAA NCEI Archives.
Supports discovery of storm archives by year and storm ID,
bounded downloading, tarball extraction, and manifest staging.
"""

import os
import re
import tarfile
from typing import Any, Dict, List, Optional
import urllib.request

from ml.data.acquisition.adapters.base_acquisition import (
    BaseAcquisitionAdapter,
    DiscoveredRemoteAsset,
)
from ml.data.acquisition.config import AcquisitionConfig
from ml.data.acquisition.downloader import DownloadExecutionResult


class HURSATAcquisitionAdapter(BaseAcquisitionAdapter):
    """Acquisition adapter for NOAA HURSAT-B1 v06 archive."""

    def __init__(self, config: Optional[AcquisitionConfig] = None):
        super().__init__("noaa_hursat_b1", config)
        self.archive_url = self.config.noaa_ncei_hursat_base

    def discover_remote_assets(self, query: Optional[Dict[str, Any]] = None) -> List[DiscoveredRemoteAsset]:
        """
        Discovers available HURSAT-B1 archives from NOAA NCEI.
        Query filters can include:
        - 'year': int (e.g. 2013, 2014, 2015)
        - 'storm_id': str (e.g. '2013279N12093')
        - 'storm_name': str (e.g. 'PHAILIN')
        """
        query = query or {}
        target_year = query.get("year")
        target_storm_id = query.get("storm_id")
        target_storm_name = query.get("storm_name")

        years_to_check = [target_year] if target_year else [2013, 2014, 2015]
        discovered: List[DiscoveredRemoteAsset] = []

        for yr in years_to_check:
            year_url = f"{self.archive_url}{yr}/"
            try:
                req = urllib.request.Request(
                    year_url,
                    headers={"User-Agent": self.config.user_agent},
                )
                with urllib.request.urlopen(req, timeout=self.config.timeout_seconds) as resp:
                    html = resp.read().decode("utf-8", errors="ignore")
                    # Pattern e.g.: HURSAT_b1_v06_2013001N04141_SONAMU_c20170721.tar.gz
                    pattern = r'href=["\'](HURSAT_b1_v06_([0-9]{4}[0-9]{3}[NS][0-9]{5})_([A-Za-z0-9_-]+)_c[0-9]+\.tar\.gz)["\']'
                    matches = re.findall(pattern, html)

                    for full_fname, sid, sname in matches:
                        if target_storm_id and target_storm_id.upper() not in sid.upper():
                            continue
                        if target_storm_name and target_storm_name.upper() not in sname.upper():
                            continue

                        discovered.append(
                            DiscoveredRemoteAsset(
                                asset_id=f"hursat_{sid}_{sname}",
                                source_id=self.source_id,
                                remote_url=f"{year_url}{full_fname}",
                                file_name=full_fname,
                                storm_id=sid,
                                storm_name=sname,
                                year=yr,
                                time_coverage=f"{yr}",
                                metadata={
                                    "archive_type": "tar.gz",
                                    "format": "NetCDF-3",
                                    "year": yr,
                                },
                            )
                        )
            except Exception as e:
                # Log discovery error without crashing
                pass

        return discovered

    def acquire_asset(
        self, asset: DiscoveredRemoteAsset, target_dir: Optional[str] = None
    ) -> DownloadExecutionResult:
        """Downloads the asset and unpacks contained NetCDF files if it is a tarball."""
        base_target_dir = target_dir or os.path.join(self.config.raw_data_dir, "hursat")
        storm_dir = os.path.join(base_target_dir, asset.storm_id or "misc")
        os.makedirs(storm_dir, exist_ok=True)

        tar_dest = os.path.join(storm_dir, asset.file_name)
        result = self.downloader.download_file(
            url=asset.remote_url,
            target_path=tar_dest,
        )

        if not result.success:
            return result

        # If tar.gz, extract .nc files
        if asset.file_name.endswith(".tar.gz") and os.path.exists(tar_dest):
            try:
                with tarfile.open(tar_dest, "r:gz") as tar:
                    for member in tar.getmembers():
                        # Protect against zip-slip directory traversal
                        if member.name.startswith("/") or ".." in member.name:
                            continue
                        if member.name.endswith(".nc"):
                            tar.extract(member, path=storm_dir)
            except Exception as e:
                result.error_message = f"Download succeeded but extraction failed: {str(e)}"

        return result
