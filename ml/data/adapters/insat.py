"""
ISRO INSAT-3D/3DR Imager Source Adapter for CycloneGuard.
Provides interface for high-resolution geostationary imagery over the North Indian Ocean basin.
Verified Operational Status:
- Anonymous public API downloads are not supported by ISRO MOSDAC.
- Access requires authenticated MOSDAC user credentials and security session tokens.
- Standard general accounts encounter a 3-day data latency for Level-1 products.
- Automated pipeline integration is staged and pending credential provisioning.
"""

from typing import Any, Dict, List, Optional
import os

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


class INSATAdapter(BaseDataSourceAdapter):
    """Adapter for ISRO INSAT-3D/3DR meteorological imager data."""

    def __init__(self):
        super().__init__("isro_insat3d_mosdac")

    def discover(self, filters: Optional[Dict[str, Any]] = None) -> List[DiscoveredResource]:
        return [
            DiscoveredResource(
                resource_id="insat3d_l1b_tir1",
                source_id=self.source_id,
                name="INSAT-3D Imager Level-1B Calibrated Radiance (TIR-1 10.8 µm)",
                remote_url="https://www.mosdac.gov.in/ (Requires authenticated session)",
                time_coverage="2013-present (30-min cadence)",
                spatial_coverage="Indian Ocean full disk (40°E-120°E, 45°S-45°N), 4 km resolution",
                format="HDF5",
                metadata={"channel": "TIR1", "wavelength_um": 10.8, "auth_required": True},
            ),
            DiscoveredResource(
                resource_id="insat3dr_l1b_tir1",
                source_id=self.source_id,
                name="INSAT-3DR Imager Level-1B Calibrated Radiance (TIR-1 10.8 µm)",
                remote_url="https://www.mosdac.gov.in/ (Requires authenticated session)",
                time_coverage="2016-present (30-min staggered with INSAT-3D for 15-min effective)",
                spatial_coverage="Indian Ocean full disk, 4 km resolution",
                format="HDF5",
                metadata={"channel": "TIR1", "wavelength_um": 10.8, "auth_required": True},
            ),
        ]

    def download(self, resource_id: str, target_dir: str) -> DownloadResult:
        """
        Reflects verified MOSDAC operational status:
        Anonymous automated downloads are not permitted.
        """
        return DownloadResult(
            source_id=self.source_id,
            resource_id=resource_id,
            status=DownloadStatus.NOT_IMPLEMENTED,
            message="Automatic ingestion not implemented: ISRO MOSDAC requires registered user authentication, API token configuration in config.json, and verified session approval. See docs/INSAT_DATA_STATUS.md.",
        )

    def validate(self, file_path: str) -> ValidationReport:
        report = ValidationReport(source_id=self.source_id, file_path=file_path, status=ValidationSeverity.VALID)
        if not os.path.exists(file_path):
            report.status = ValidationSeverity.ERROR
            report.checks.append(ValidationCheck(
                check_name="file_exists",
                passed=False,
                severity=ValidationSeverity.ERROR,
                message=f"INSAT file not found: {file_path}",
            ))
            report.summary = "File does not exist."
            return report

        report.checks.append(ValidationCheck(
            check_name="file_exists",
            passed=True,
            severity=ValidationSeverity.VALID,
            message="File exists.",
        ))
        report.summary = "INSAT local file validated."
        return report

    def parse(self, file_path: str) -> ParsedData:
        return ParsedData(
            source_id=self.source_id,
            file_path=file_path,
            records_count=0,
            raw_variables=["IMG_TIR1", "IMG_TIR2", "IMG_MIR", "IMG_WV", "IMG_VIS"],
            raw_dimensions={},
            data_payload={},
        )

    def normalize(self, parsed_data: ParsedData) -> NormalizedData:
        return NormalizedData(
            source_id=self.source_id,
            normalized_type="satellite_observation",
            records_count=0,
            data_payload={},
            units={
                "IMG_TIR1": "Kelvin (Brightness Temperature 10.8 µm)",
                "IMG_TIR2": "Kelvin (Brightness Temperature 12.0 µm)",
                "IMG_WV": "Kelvin (Water Vapor 6.7 µm)",
            },
            normalization_log=["INSAT normalization pipeline staged for HDF5 ingestion."],
        )
