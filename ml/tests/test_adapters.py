"""
Unit tests for data source adapters.
"""

import os
# pyrefly: ignore [missing-import]
import pytest

from ml.data.adapters.base import BaseDataSourceAdapter
from ml.data.adapters.ibtracs import IBTrACSAdapter
from ml.data.adapters.hursat import HURSATAdapter
from ml.data.adapters.adt import ADTHursatAdapter
from ml.data.adapters.insat import INSATAdapter
from ml.data.adapters.scatterometer import ScatterometerAdapter
from ml.data.adapters.microwave import MicrowaveAdapter
from ml.data.schemas.adapter_results import DownloadStatus, ValidationSeverity


def test_adapter_discovery_contracts():
    adapters = [
        IBTrACSAdapter(),
        HURSATAdapter(),
        ADTHursatAdapter(),
        INSATAdapter(),
        ScatterometerAdapter(),
        MicrowaveAdapter(),
    ]
    for a in adapters:
        res = a.discover()
        assert len(res) > 0
        assert all(r.source_id == a.source_id for r in res)


def test_unimplemented_downloads_report_honestly():
    # Sources without automated public anonymous download should report NOT_IMPLEMENTED honestly
    insat = INSATAdapter()
    res = insat.download("insat3d_l1b_tir1", "/tmp")
    assert res.status == DownloadStatus.NOT_IMPLEMENTED
    assert "MOSDAC" in res.message or "authentication" in res.message

    hursat = HURSATAdapter()
    res_h = hursat.download("hursat_b1_global_v06", "/tmp")
    assert res_h.status == DownloadStatus.NOT_IMPLEMENTED


def test_ibtracs_adapter_with_sample():
    sample_path = "data/samples/ibtracs_sample_ni.csv"
    if not os.path.exists(sample_path):
        pytest.skip("Sample file not present")

    adapter = IBTrACSAdapter()
    report = adapter.validate(sample_path)
    assert report.status in (ValidationSeverity.VALID, ValidationSeverity.WARNING)

    parsed = adapter.parse(sample_path)
    assert parsed.records_count > 0

    norm = adapter.normalize(parsed)
    assert norm.records_count > 0
    assert "2023129N08091" in norm.data_payload  # Cyclone Mocha


def test_hursat_adapter_with_sample():
    sample_path = "data/samples/hursat_b1_sample_mocha.nc"
    if not os.path.exists(sample_path):
        pytest.skip("Sample file not present")

    adapter = HURSATAdapter()
    report = adapter.validate(sample_path)
    assert report.status == ValidationSeverity.VALID

    parsed = adapter.parse(sample_path)
    assert "IRWIN" in parsed.raw_variables

    norm = adapter.normalize(parsed)
    assert norm.data_payload["metadata"].source_id == "noaa_hursat_b1"
    assert "IRWIN" in norm.data_payload["arrays"]
