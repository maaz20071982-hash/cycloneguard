"""
Passive Microwave Source Adapter for CycloneGuard.
Covers GPM Microwave Imager (GMI), AMSR2, and SSMIS sensors.
Role: Penetrates upper cirrus canopy to image deep eyewall convection, concentric eyewall cycles (ERC),
and internal precipitation cores using 37 GHz and 85-91 GHz brightness temperatures.
"""

import os
from typing import Any, Dict, List, Optional

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


class MicrowaveAdapter(BaseDataSourceAdapter):
    """Adapter for passive microwave satellite radiometer observations."""

    def __init__(self):
        super().__init__("gpm_gmi_microwave")

    def discover(self, filters: Optional[Dict[str, Any]] = None) -> List[DiscoveredResource]:
        return [
            DiscoveredResource(
                resource_id="gpm_gmi_l1b_rad",
                source_id=self.source_id,
                name="GPM Microwave Imager (GMI) Level-1B Calibrated Brightness Temperatures",
                remote_url="https://disc.gsfc.nasa.gov/ (NASA GES DISC)",
                time_coverage="2014-present",
                spatial_coverage="Global Tropical Swaths (65°S to 65°N)",
                format="HDF5",
                metadata={"frequencies_ghz": [10.65, 18.7, 36.5, 89.0, 166.0, 183.3]},
            )
        ]

    def download(self, resource_id: str, target_dir: str) -> DownloadResult:
        return DownloadResult(
            source_id=self.source_id,
            resource_id=resource_id,
            status=DownloadStatus.NOT_IMPLEMENTED,
            message="Automatic ingestion not implemented: GPM/microwave data requires NASA Earthdata authenticated credentials (.netrc).",
        )

    def validate(self, file_path: str) -> ValidationReport:
        report = ValidationReport(source_id=self.source_id, file_path=file_path, status=ValidationSeverity.VALID)
        if not os.path.exists(file_path):
            report.status = ValidationSeverity.ERROR
            report.checks.append(ValidationCheck(
                check_name="file_exists",
                passed=False,
                severity=ValidationSeverity.ERROR,
                message=f"Microwave file not found: {file_path}",
            ))
            report.summary = "File does not exist."
            return report

        report.checks.append(ValidationCheck(
            check_name="file_exists",
            passed=True,
            severity=ValidationSeverity.VALID,
            message="File exists.",
        ))
        report.summary = "Microwave file check complete."
        return report

    def parse(self, file_path: str) -> ParsedData:
        return ParsedData(
            source_id=self.source_id,
            file_path=file_path,
            records_count=0,
            raw_variables=["Tc_37GHz_V", "Tc_37GHz_H", "Tc_89GHz_V", "Tc_89GHz_H"],
            raw_dimensions={},
            data_payload={},
        )

    def normalize(self, parsed_data: ParsedData) -> NormalizedData:
        return NormalizedData(
            source_id=self.source_id,
            normalized_type="microwave_observation",
            records_count=0,
            data_payload={},
            units={
                "Tc_37GHz": "Kelvin (Brightness temperature sensitive to liquid water / rain)",
                "Tc_89GHz": "Kelvin (Brightness temperature sensitive to ice scattering / deep convection)",
            },
            normalization_log=["Microwave observations staged as high-frequency convective structure layer."],
        )
