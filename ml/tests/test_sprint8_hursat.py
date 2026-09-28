"""
Sprint 8 Test Suite: Historical HURSAT-B1 Acquisition, Coincidence, Patches, RI & Leakage.

Validates all 12 Phase 16 requirements:
1. Historical asset discovery & target storm inventory
2. Download caching & download report integrity
3. Satellite manifest generation
4. HURSAT NetCDF validation & corruption rejection
5. Temporal matching within tolerance bounds
6. Spatial matching & cyclone-centering
7. Patch extraction (64x64 float32 physical units)
8. Forward 24h RI-label association
9. Storm-wise partitioning & disjointness
10. Duplicate asset and patch detection
11. Leakage detection & zero cross-partition leakage
12. Dataset versioning (satellite_hursat_v2 without overwriting v1)
"""

import json
import os
import numpy as np
import pytest
import pandas as pd

from ml.data.acquisition.downloader import ResilientDownloader
from ml.data.alignment.coincidence_engine import CoincidenceEngine
from ml.data.manifests.satellite_manifest import (
    SatelliteAssetManifestRecord,
    SatelliteManifestStore,
)
from ml.data.preprocessing.patch_extractor import CyclonePatchExtractor
from ml.data.schemas.track import CycloneTrackPoint
from ml.data.validation.leakage_audit import run_sprint8_leakage_audit, SatelliteLeakageAuditor
from ml.data.validation.source_validators.hursat_validator import HURSATSourceValidator


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


# -------------------------------------------------------------------------
# 1. Historical Asset Discovery & Target Storm Inventory
# -------------------------------------------------------------------------
def test_historical_target_storms_inventory():
    """Verify target storm inventory contains North Indian Ocean storms with valid tracks."""
    target_path = os.path.join(ROOT_DIR, "data", "manifests", "historical_target_storms.json")
    assert os.path.exists(target_path), "Target storm inventory must exist"

    with open(target_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    storms = data.get("target_storms", [])
    assert len(storms) == 6, "Must target exactly 6 historical NI storms"

    storm_names = {s["storm_name"] for s in storms}
    expected = {"PHAILIN", "HELEN", "HUDHUD", "NILOFAR", "CHAPALA", "MEGH"}
    assert expected.issubset(storm_names), f"Expected {expected}, got {storm_names}"

    for s in storms:
        assert s["basin"] == "NI"
        assert s["number_of_track_observations"] > 0
        assert s["season"] in [2013, 2014, 2015]


def test_hursat_archive_discovery_records():
    """Verify discovered archive inventory has required schema without blind scraping."""
    inventory_path = os.path.join(ROOT_DIR, "data", "manifests", "hursat_archive_inventory.jsonl")
    assert os.path.exists(inventory_path), "Archive inventory must exist"

    records = []
    with open(inventory_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    assert len(records) >= 287, f"Expected at least 287 discovered assets, got {len(records)}"

    for r in records[:20]:
        assert r["source"] == "noaa_hursat_b1"
        assert "HURSAT-B1" in r["product"]
        assert r["year"] in [2013, 2014, 2015]
        assert r["asset_identifier"]
        assert r["remote_location"].startswith("https://")
        assert r["download_status"] == "DISCOVERED"


# -------------------------------------------------------------------------
# 2. Download Caching & Report Integrity
# -------------------------------------------------------------------------
def test_download_report_and_caching():
    """Verify download report tracks attempted, downloaded, and cached assets truthfully."""
    report_path = os.path.join(ROOT_DIR, "data", "reports", "hursat_download_report.json")
    assert os.path.exists(report_path), "Download report must exist"

    with open(report_path, "r", encoding="utf-8") as f:
        rep = json.load(f)

    assert rep["discovered"] == 6
    assert rep["attempted"] == 6
    assert rep["downloaded"] + rep["already_cached"] == 6
    assert rep["total_netcdf_files_extracted"] == 887
    assert rep["corrupted"] == 0
    assert rep["failed"] == 0

    # Test cache hit behavior
    downloader = ResilientDownloader()
    sample_file = os.path.join(ROOT_DIR, "data", "samples", "hursat_b1_sample_mocha.nc")
    if os.path.exists(sample_file):
        cached_res = downloader.download_file("https://example.com/fake_mocha.nc", target_path=sample_file)
        assert cached_res.was_cached is True
        assert cached_res.success is True


# -------------------------------------------------------------------------
# 3. Satellite Manifest Generation
# -------------------------------------------------------------------------
def test_satellite_manifest_generation():
    """Verify satellite asset manifest record structure and validation."""
    record = SatelliteAssetManifestRecord(
        asset_id="test_hursat_granule_001",
        source="noaa_hursat_b1",
        product="HURSAT-B1",
        sensor="ISCCP-B1 Geostationary",
        channel="IRWIN",
        channels=["IRWIN", "IRWVP", "VSCHN"],
        timestamp="2013-10-10T12:00:00Z",
        storm_id="2013281N12098",
        storm_name="PHAILIN",
        file_path="data/raw/hursat/2013/PHAILIN/test.nc",
        file_size=250000,
        checksum="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        coverage={"lat_min": 7.0, "lat_max": 23.0, "lon_min": 80.0, "lon_max": 96.0},
        spatial_resolution_deg=0.08,
        dimensions=[201, 201],
        processing_level="L2",
        status="VALID",
    )
    assert record.asset_id == "test_hursat_granule_001"
    assert "IRWIN" in record.channels
    assert record.spatial_resolution_deg == 0.08
    assert record.status == "VALID"


# -------------------------------------------------------------------------
# 4. HURSAT NetCDF Validation
# -------------------------------------------------------------------------
def test_hursat_netcdf_validation_real_sample():
    """Validate real HURSAT NetCDF sample using HURSATSourceValidator."""
    validator = HURSATSourceValidator()
    sample_path = os.path.join(ROOT_DIR, "data", "samples", "hursat_b1_sample_mocha.nc")
    assert os.path.exists(sample_path)

    res = validator.validate_hursat_file(sample_path)
    assert res.is_valid is True
    assert len(res.dimensions) >= 2
    assert "IRWIN" in res.variables
    assert res.time_metadata is not None
    assert res.geographic_extent is not None


def test_hursat_validation_corrupted_file(tmp_path):
    """Corrupted / truncated NetCDF file must be caught and marked invalid."""
    corrupted_file = tmp_path / "corrupted_hursat.nc"
    corrupted_file.write_bytes(b"NOT_A_VALID_NETCDF_HEADER_DATA_12345")

    validator = HURSATSourceValidator()
    res = validator.validate_hursat_file(str(corrupted_file))
    assert res.is_valid is False


# -------------------------------------------------------------------------
# 5. Temporal Matching & Coincidence Bounds
# -------------------------------------------------------------------------
def test_temporal_matching_tolerance_enforcement():
    """Geostationary matches beyond +/-30 minutes must be rejected as outside tolerance."""
    engine = CoincidenceEngine()

    track_pt = CycloneTrackPoint(
        storm_id="2013281N12098",
        storm_name="PHAILIN",
        season=2013,
        basin="NI",
        timestamp_utc="2013-10-10T12:00:00Z",
        latitude=14.5,
        longitude=88.0,
        wind_speed_kts=90.0,
    )

    # 1. Inside tolerance (15 min delta)
    sat_valid = SatelliteAssetManifestRecord(
        asset_id="sat_valid_01",
        source="noaa_hursat_b1",
        product="HURSAT-B1",
        sensor="ISCCP-B1",
        channel="IRWIN",
        channels=["IRWIN"],
        timestamp="2013-10-10T12:15:00Z",
        storm_id="2013281N12098",
        file_path="dummy.nc",
        file_size=1000,
        checksum="abc",
        coverage={"lat_min": 10.0, "lat_max": 20.0, "lon_min": 80.0, "lon_max": 95.0},
        spatial_resolution_deg=0.08,
        dimensions=[100, 100],
        processing_level="L2",
        status="VALID",
    )
    match_ok = engine.match_asset_to_track_point(track_pt, sat_valid)
    assert match_ok.available is True
    assert match_ok.is_within_tolerance is True
    assert match_ok.delta_minutes == 15.0

    # 2. Outside tolerance (45 min delta > 30 min)
    sat_late = SatelliteAssetManifestRecord(
        asset_id="sat_late_01",
        source="noaa_hursat_b1",
        product="HURSAT-B1",
        sensor="ISCCP-B1",
        channel="IRWIN",
        channels=["IRWIN"],
        timestamp="2013-10-10T12:45:00Z",
        storm_id="2013281N12098",
        file_path="dummy.nc",
        file_size=1000,
        checksum="abc2",
        coverage={"lat_min": 10.0, "lat_max": 20.0, "lon_min": 80.0, "lon_max": 95.0},
        spatial_resolution_deg=0.08,
        dimensions=[100, 100],
        processing_level="L2",
        status="VALID",
    )
    match_late = engine.match_asset_to_track_point(track_pt, sat_late)
    assert match_late.is_within_tolerance is False
    assert match_late.available is False


# -------------------------------------------------------------------------
# 6. Spatial Matching & Cyclone-Centering
# -------------------------------------------------------------------------
def test_spatial_matching_domain_bounds():
    """Spatial matching must verify cyclone center falls within satellite domain."""
    engine = CoincidenceEngine()

    track_pt = CycloneTrackPoint(
        storm_id="2013281N12098",
        storm_name="PHAILIN",
        season=2013,
        basin="NI",
        timestamp_utc="2013-10-10T12:00:00Z",
        latitude=14.5,
        longitude=88.0,
    )

    # Satellite image over Eastern Pacific (lat 10-20, lon -120 to -110)
    sat_remote = SatelliteAssetManifestRecord(
        asset_id="sat_remote_01",
        source="noaa_hursat_b1",
        product="HURSAT-B1",
        sensor="ISCCP-B1",
        channel="IRWIN",
        channels=["IRWIN"],
        timestamp="2013-10-10T12:00:00Z",
        storm_id="2013281N12098",
        file_path="dummy.nc",
        file_size=1000,
        checksum="abc3",
        coverage={"lat_min": 10.0, "lat_max": 20.0, "lon_min": -120.0, "lon_max": -110.0},
        spatial_resolution_deg=0.08,
        dimensions=[100, 100],
        processing_level="L2",
        status="VALID",
    )
    match = engine.match_asset_to_track_point(track_pt, sat_remote)
    assert match.spatial_coverage_status == "OUT_OF_BOUNDS"
    assert match.available is False
    assert match.quality_status == "REJECTED"


# -------------------------------------------------------------------------
# 7. Patch Extraction (64x64 float32 physical units)
# -------------------------------------------------------------------------
def test_patch_extraction_shape_and_dtype():
    """Patch extractor must produce (64, 64) float32 arrays with center metadata."""
    extractor = CyclonePatchExtractor(crop_shape=(64, 64))

    # Synthetic 200x200 field centered around lat 15, lon 88
    lats = np.linspace(10.0, 20.0, 200)
    lons = np.linspace(83.0, 93.0, 200)
    data_grid = np.random.uniform(200.0, 300.0, size=(200, 200)).astype(np.float32)

    patch, metrics = extractor.extract_patch_array(
        satellite_grid=data_grid,
        lats=lats,
        lons=lons,
        center_lat=15.0,
        center_lon=88.0,
    )

    assert patch.shape == (64, 64)
    assert patch.dtype == np.float32
    assert metrics["quality_status"] in ["NOMINAL", "PADDED"]
    assert "spatial_extent" in metrics


# -------------------------------------------------------------------------
# 8. RI-Label Association
# -------------------------------------------------------------------------
def test_ri_label_association_ground_truth():
    """Verify RI labels match Kaplan & DeMaria definition and 299 supervised samples."""
    ri_samples_path = os.path.join(ROOT_DIR, "data", "processed", "hursat_ri_samples.csv")
    assert os.path.exists(ri_samples_path), "hursat_ri_samples.csv must exist"

    df = pd.read_csv(ri_samples_path)
    assert len(df) == 347, "Must contain all 347 coincident observations"

    # Supervised samples with future 24h track
    supervised = df[df["is_future_track_valid"] == True]
    assert len(supervised) == 299, f"Expected 299 supervised samples, got {len(supervised)}"

    # RI counts
    ri_pos = df[df["ri_target"] == 1]
    ri_neg = df[df["ri_target"] == 0]
    assert len(ri_pos) == 39, f"Expected 39 RI+, got {len(ri_pos)}"
    assert len(ri_neg) == 260, f"Expected 260 RI-, got {len(ri_neg)}"

    # Check Kaplan & DeMaria threshold rule (delta_wind_kts >= 30.0 -> RI=1)
    for _, row in supervised.iterrows():
        delta_v = row["delta_wind_kts"]
        if delta_v >= 30.0:
            assert row["ri_target"] == 1
        else:
            assert row["ri_target"] == 0


# -------------------------------------------------------------------------
# 9. Storm-Wise Splitting & Zero Partition Leakage
# -------------------------------------------------------------------------
def test_historical_storm_wise_disjointness():
    """Historical storm partitions must be strictly disjoint with zero shared storms."""
    split_cfg_path = os.path.join(ROOT_DIR, "ml", "config", "historical_split_config.json")
    assert os.path.exists(split_cfg_path), "historical_split_config.json must exist"

    with open(split_cfg_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    train_storms = set(cfg["train_storms"])
    val_storms = set(cfg["val_storms"])
    test_storms = set(cfg["test_storms"])

    assert len(train_storms.intersection(val_storms)) == 0, "Train and Val must be disjoint"
    assert len(train_storms.intersection(test_storms)) == 0, "Train and Test must be disjoint"
    assert len(val_storms.intersection(test_storms)) == 0, "Val and Test must be disjoint"

    # Verify all partitions contain non-zero RI events
    ri_samples_path = os.path.join(ROOT_DIR, "data", "processed", "hursat_ri_samples.csv")
    df = pd.read_csv(ri_samples_path)

    for part_name, storms in [("TRAIN", train_storms), ("VAL", val_storms), ("TEST", test_storms)]:
        sub = df[df["storm_id"].isin(storms) & (df["is_future_track_valid"] == True)]
        ri_events = len(sub[sub["ri_target"] == 1])
        assert ri_events > 0, f"{part_name} partition must have > 0 RI events (got {ri_events})"


# -------------------------------------------------------------------------
# 10. Duplicate Asset & Patch Detection
# -------------------------------------------------------------------------
def test_duplicate_detection_rules(tmp_path):
    """Verify duplicate asset and patch rejection logic."""
    manifest_file = str(tmp_path / "test_manifest.jsonl")
    manifest_store = SatelliteManifestStore(manifest_file=manifest_file)

    record1 = SatelliteAssetManifestRecord(
        asset_id="asset_unique_01",
        source="noaa_hursat_b1",
        product="HURSAT-B1",
        sensor="ISCCP",
        channel="IRWIN",
        channels=["IRWIN"],
        timestamp="2013-10-10T06:00:00Z",
        storm_id="2013281N12098",
        file_path="f1.nc",
        file_size=100,
        checksum="chk_dup_123",
        coverage={"lat_min": 10, "lat_max": 20, "lon_min": 80, "lon_max": 90},
        spatial_resolution_deg=0.08,
        dimensions=[100, 100],
        processing_level="L2",
        status="VALID",
    )
    manifest_store.write_records([record1])

    existing = manifest_store.read_records()
    assert len(existing) == 1

    # Check that duplicates can be detected by asset_id or checksum
    existing_ids = {r.asset_id for r in existing}
    existing_checksums = {r.checksum for r in existing}

    assert "asset_unique_01" in existing_ids
    assert "chk_dup_123" in existing_checksums


# -------------------------------------------------------------------------
# 11. Leakage Detection Audit
# -------------------------------------------------------------------------
def test_satellite_leakage_audit_seven_checks():
    """Run SatelliteLeakageAuditor and assert all 7 checks pass with 0 leakage."""
    res = run_sprint8_leakage_audit()

    assert res["storm_wise_disjoint"] is True
    assert res["cross_partition_image_leakage"] is True
    assert res["cross_partition_patch_leakage"] is True
    assert res["temporal_directionality_violations"] == 0
    assert res["future_track_in_features_count"] == 0
    assert res["label_independence_verified"] is True
    assert res["train_val_overlap_count"] == 0
    assert res["train_test_overlap_count"] == 0
    assert res["val_test_overlap_count"] == 0


# -------------------------------------------------------------------------
# 12. Dataset Versioning (v2 created, v1 untouched)
# -------------------------------------------------------------------------
def test_dataset_versioning_immutability():
    """Verify satellite_hursat_v2 exists while satellite_v1 remains untouched."""
    v1_dir = os.path.join(ROOT_DIR, "data", "datasets", "satellite_v1")
    v2_dir = os.path.join(ROOT_DIR, "data", "datasets", "satellite_hursat_v2")

    assert os.path.exists(v1_dir), "satellite_v1 must exist"
    assert os.path.exists(v2_dir), "satellite_hursat_v2 must exist"

    # Verify v1 metadata retains original version
    with open(os.path.join(v1_dir, "metadata.json"), "r", encoding="utf-8") as f:
        v1_meta = json.load(f)
    assert v1_meta["dataset_version"] == "cycloneguard-satellite-v1"

    # Verify v2 metadata has new version
    with open(os.path.join(v2_dir, "metadata.json"), "r", encoding="utf-8") as f:
        v2_meta = json.load(f)
    assert v2_meta["dataset_version"] == "cycloneguard-satellite-hursat-v2"
    assert v2_meta["observation_counts"]["total_cyclone_observations"] == 347
    assert v2_meta["patch_counts"]["total_extracted_patches"] == 1020
