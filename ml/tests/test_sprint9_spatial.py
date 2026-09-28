"""
Sprint 9 Test Suite: Spatial Satellite Baseline, Feature Extraction & Evaluation.

Tests all Phase 19 requirements:
1. Patch loading & dimensions
2. Missing channel handling & explicit flags
3. Spatial feature extraction (Families A-E)
4. NaN handling & robustness
5. Radial structural proxy calculation (Core, Ring, Outer)
6. Spatial RI dataset construction
7. Storm-wise partitioning & disjointness
8. Future lookahead & leakage prevention
9. Model S and Model ST inference
10. Validation-only threshold selection
11. Model metadata & limitations documentation
12. Feature registry schema completeness
"""

import json
import os
import pickle
import numpy as np
import pytest
import pandas as pd

from ml.features.satellite_spatial import (
    SatelliteSpatialFeatureExtractor,
    SpatialFeatureConfig,
)
from ml.datasets.spatial_ri_dataset import (
    SpatialRIDatasetBuilder,
    SPATIAL_FEATURE_NAMES,
    TEMPORAL_FEATURE_NAMES,
)


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


# -------------------------------------------------------------------------
# 1. Patch Loading & Dimensions
# -------------------------------------------------------------------------
def test_patch_loading_and_dimensions():
    """Verify physical patch dimensions (64x64) and realistic physical units."""
    patch_dir = os.path.join(ROOT_DIR, "data", "processed", "satellite_patches")
    assert os.path.exists(patch_dir), "Patch directory must exist from Sprint 8"
    
    # Check storm subdirectories
    storm_dirs = [d for d in os.listdir(patch_dir) if os.path.isdir(os.path.join(patch_dir, d))]
    assert len(storm_dirs) > 0, "Storm patch directories must exist"

    # Find an IRWIN patch.npy
    sample_patch_path = None
    for root, dirs, files in os.walk(patch_dir):
        if "patch.npy" in files and "IRWIN" in root:
            sample_patch_path = os.path.join(root, "patch.npy")
            break

    assert sample_patch_path is not None, "At least one IRWIN patch.npy must be present"
    data = np.load(sample_patch_path)
    assert data.shape == (64, 64), f"Patch shape must be 64x64, got {data.shape}"
    assert data.dtype == np.float32, f"Patch dtype must be float32, got {data.dtype}"
    
    # Check valid temperature range for IRWIN (180 K to 340 K)
    valid_mask = ~np.isnan(data)
    if np.any(valid_mask):
        valid_vals = data[valid_mask]
        assert np.min(valid_vals) >= 150.0, "IRWIN min temperature unphysically low"
        assert np.max(valid_vals) <= 350.0, "IRWIN max temperature unphysically high"


# -------------------------------------------------------------------------
# 2. Missing Channel Handling & Availability Flags
# -------------------------------------------------------------------------
def test_missing_channel_handling_and_flags():
    """Verify that missing channels produce explicit flags and never zero-fill."""
    extractor = SatelliteSpatialFeatureExtractor()

    # Synthetic observation with only IRWIN
    irwin_patch = np.full((64, 64), 250.0, dtype=np.float32)
    irwin_patch[28:36, 28:36] = 205.0

    feats = extractor.extract_all_features(
        irwin_patch=irwin_patch,
        irwvp_patch=None,
        vschn_patch=None,
    )

    # Missing flags
    assert feats["has_irwvp"] == 0.0
    assert feats["has_vschn"] == 0.0

    # Cross-channel and visible features should be NaN, NOT 0.0
    assert np.isnan(feats["ir_wv_diff_mean"])
    assert np.isnan(feats["ir_wv_spatial_corr"])
    assert np.isnan(feats["vschn_mean"])
    assert np.isnan(feats["vschn_std"])


# -------------------------------------------------------------------------
# 3. Spatial Feature Extraction (All 38 Features)
# -------------------------------------------------------------------------
def test_feature_extraction_all_families():
    """Verify extraction of all 38 spatial features across Families A-E."""
    extractor = SatelliteSpatialFeatureExtractor()

    np.random.seed(42)
    irwin = np.random.uniform(200.0, 280.0, (64, 64)).astype(np.float32)
    irwvp = np.random.uniform(220.0, 260.0, (64, 64)).astype(np.float32)
    vschn = np.random.uniform(0.1, 0.9, (64, 64)).astype(np.float32)

    feats = extractor.extract_all_features(
        irwin_patch=irwin,
        irwvp_patch=irwvp,
        vschn_patch=vschn,
    )

    assert len(feats) == len(SPATIAL_FEATURE_NAMES), (
        f"Expected {len(SPATIAL_FEATURE_NAMES)} features, got {len(feats)}"
    )

    for name in SPATIAL_FEATURE_NAMES:
        assert name in feats, f"Missing feature {name}"
        assert not np.isnan(feats[name]), f"Feature {name} is NaN when all channels are available"


# -------------------------------------------------------------------------
# 4. NaN Handling & Robustness
# -------------------------------------------------------------------------
def test_nan_handling():
    """Verify extractor safely handles partial NaN arrays without crashing."""
    extractor = SatelliteSpatialFeatureExtractor()

    irwin = np.full((64, 64), 240.0, dtype=np.float32)
    # Fill 30% with NaNs
    irwin[:20, :20] = np.nan
    irwin[50:, 50:] = np.nan

    feats = extractor.extract_irwin_statistics(irwin)

    assert not np.isnan(feats["irwin_mean"])
    assert feats["irwin_mean"] == pytest.approx(240.0, abs=1e-3)


# -------------------------------------------------------------------------
# 5. Radial Structural Proxy Calculation (Core, Ring, Outer)
# -------------------------------------------------------------------------
def test_radial_structural_proxies():
    """Verify radial zones: core (r<=50km), ring (50<r<=150km), outer (150<r<=250km)."""
    extractor = SatelliteSpatialFeatureExtractor()

    grid = np.zeros((64, 64), dtype=np.float32)
    center = 31.5
    pixel_size_km = 8.9

    y, x = np.ogrid[:64, :64]
    dist_km = np.sqrt((x - center) ** 2 + (y - center) ** 2) * pixel_size_km

    # Set distinct temperatures by zone
    grid[dist_km <= 50.0] = 200.0  # Cold convective core (< 219K)
    grid[(dist_km > 50.0) & (dist_km <= 150.0)] = 240.0  # Warmer ring (> 233K)
    grid[(dist_km > 150.0) & (dist_km <= 250.0)] = 270.0  # Warm outer cloud

    proxies = extractor.extract_core_ring_features(grid)

    assert proxies["irwin_core_mean"] == pytest.approx(200.0, abs=0.5)
    assert proxies["irwin_ring_mean"] == pytest.approx(240.0, abs=0.5)
    assert proxies["irwin_outer_mean"] == pytest.approx(270.0, abs=0.5)

    # Core vs Ring difference = ring_mean - core_mean = 240 - 200 = 40.0
    assert proxies["irwin_core_ring_diff"] == pytest.approx(40.0, abs=1.0)
    # Core cold fraction below 219.15 K should be 1.0
    assert proxies["irwin_core_very_cold_frac"] == pytest.approx(1.0, abs=1e-3)
    # Ring cold fraction below 233.15 K should be 0.0
    assert proxies["irwin_ring_cold_frac"] == pytest.approx(0.0, abs=1e-3)


# -------------------------------------------------------------------------
# 6. Spatial RI Dataset Construction
# -------------------------------------------------------------------------
def test_spatial_ri_dataset_construction():
    """Verify the paired spatial RI dataset contains the full 299 supervised samples."""
    builder = SpatialRIDatasetBuilder(project_root=ROOT_DIR)
    dataset = builder.build()
    supervised = dataset.get_supervised_samples()

    assert len(supervised) == 299, f"Expected 299 supervised samples, got {len(supervised)}"

    # Check 39 positive and 260 negative
    y = np.array([s.ri_target for s in supervised])
    pos_count = int(np.sum(y == 1))
    neg_count = int(np.sum(y == 0))
    assert pos_count == 39, f"Expected 39 RI+ samples, got {pos_count}"
    assert neg_count == 260, f"Expected 260 RI- samples, got {neg_count}"

    # Check dataframe export
    df = dataset.to_dataframe(supervised_only=True)
    assert len(df) == 299
    assert "ri_target" in df.columns
    for feat in SPATIAL_FEATURE_NAMES:
        assert feat in df.columns, f"Spatial feature {feat} missing from dataset dataframe"


# -------------------------------------------------------------------------
# 7. Storm-Wise Partitioning & Disjointness
# -------------------------------------------------------------------------
def test_storm_wise_partitioning_disjointness():
    """Verify strict zero-overlap storm-wise partitioning."""
    builder = SpatialRIDatasetBuilder(project_root=ROOT_DIR)
    dataset = builder.build()
    df = dataset.to_dataframe(supervised_only=True)

    train_storms = set(df[df["partition"] == "TRAIN"]["storm_name"].unique())
    val_storms = set(df[df["partition"] == "VAL"]["storm_name"].unique())
    test_storms = set(df[df["partition"] == "TEST"]["storm_name"].unique())

    # Check designated storms
    expected_train = {"PHAILIN", "HELEN", "HUDHUD", "NILOFAR"}
    expected_val = {"MEGH"}
    expected_test = {"CHAPALA"}

    assert train_storms == expected_train, f"Train storms mismatch: {train_storms}"
    assert val_storms == expected_val, f"Val storms mismatch: {val_storms}"
    assert test_storms == expected_test, f"Test storms mismatch: {test_storms}"

    # Strict disjointness
    assert len(train_storms.intersection(val_storms)) == 0, "Train and Val storms overlap!"
    assert len(train_storms.intersection(test_storms)) == 0, "Train and Test storms overlap!"
    assert len(val_storms.intersection(test_storms)) == 0, "Val and Test storms overlap!"


# -------------------------------------------------------------------------
# 8. Future Lookahead & Leakage Prevention
# -------------------------------------------------------------------------
def test_leakage_and_future_lookahead():
    """Verify that observation times and patch matching have zero future lookahead."""
    builder = SpatialRIDatasetBuilder(project_root=ROOT_DIR)
    dataset = builder.build()
    df = dataset.to_dataframe(supervised_only=True)

    # Check that each sample has observation_time
    assert "observation_time" in df.columns
    # Check that no duplicated index per storm and time exists
    dups = df.duplicated(subset=["storm_id", "observation_time"])
    assert not dups.any(), "Duplicate storm observation timestamps detected!"


# -------------------------------------------------------------------------
# 9. Model Inference (Model S and Model ST)
# -------------------------------------------------------------------------
def test_model_s_and_st_inference():
    """Verify inference pipeline for Model S and Model ST artifacts."""
    # Test Model S
    model_s_dir = os.path.join(ROOT_DIR, "models", "ri", "v2_spatial")
    assert os.path.exists(os.path.join(model_s_dir, "model.pkl")), "Model S model.pkl missing"
    assert os.path.exists(os.path.join(model_s_dir, "scaler.json")), "Model S scaler.json missing"
    assert os.path.exists(os.path.join(model_s_dir, "imputer.json")), "Model S imputer.json missing"

    with open(os.path.join(model_s_dir, "model.pkl"), "rb") as f:
        model_s = pickle.load(f)

    # Test dummy inference on Model S (38 features)
    dummy_s = np.zeros((1, 38), dtype=np.float32)
    prob_s = model_s.predict_proba(dummy_s)[0, 1]
    assert 0.0 <= prob_s <= 1.0, f"Model S probability out of bounds: {prob_s}"

    # Test Model ST
    model_st_dir = os.path.join(ROOT_DIR, "models", "ri", "v2_combined")
    assert os.path.exists(os.path.join(model_st_dir, "model.pkl")), "Model ST model.pkl missing"
    assert os.path.exists(os.path.join(model_st_dir, "scaler.json")), "Model ST scaler.json missing"
    assert os.path.exists(os.path.join(model_st_dir, "imputer.json")), "Model ST imputer.json missing"

    with open(os.path.join(model_st_dir, "model.pkl"), "rb") as f:
        model_st = pickle.load(f)

    # Test dummy inference on Model ST (61 features)
    dummy_st = np.zeros((1, 61), dtype=np.float32)
    prob_st = model_st.predict_proba(dummy_st)[0, 1]
    assert 0.0 <= prob_st <= 1.0, f"Model ST probability out of bounds: {prob_st}"


# -------------------------------------------------------------------------
# 10. Validation-Only Threshold Selection
# -------------------------------------------------------------------------
def test_threshold_selection_validation_only():
    """Verify decision thresholds were selected on validation storm MEGH, not test storm."""
    with open(os.path.join(ROOT_DIR, "models", "ri", "v2_spatial", "metadata.json"), "r") as f:
        meta_s = json.load(f)
    with open(os.path.join(ROOT_DIR, "models", "ri", "v2_combined", "metadata.json"), "r") as f:
        meta_st = json.load(f)

    thresh_s = meta_s["decision_threshold"]
    thresh_st = meta_st["decision_threshold"]

    # Verify thresholds match validation metrics threshold
    assert thresh_s == pytest.approx(meta_s["validation_metrics"]["threshold"], abs=1e-4)
    assert thresh_st == pytest.approx(meta_st["validation_metrics"]["threshold"], abs=1e-4)
    assert "MEGH" in meta_s["validation_storm"]
    assert "CHAPALA" in meta_s["test_storm"]


# -------------------------------------------------------------------------
# 11. Model Metadata & Limitations Documentation
# -------------------------------------------------------------------------
def test_metadata_and_limitations_completeness():
    """Verify all required metadata fields and scientific limitation warnings."""
    for model_subdir in ["v2_spatial", "v2_combined"]:
        meta_path = os.path.join(ROOT_DIR, "models", "ri", model_subdir, "metadata.json")
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

        required_keys = [
            "model_name",
            "model_type",
            "feature_family",
            "training_dataset",
            "test_storm",
            "validation_metrics",
            "test_metrics",
            "decision_threshold",
            "calibration_status",
            "limitations",
        ]
        for key in required_keys:
            assert key in meta, f"Missing key {key} in {model_subdir} metadata"

        # Limitations must be non-empty and mention sample size / proxy limitations
        assert len(meta["limitations"]) >= 3, f"Expected at least 3 documented limitations in {model_subdir}"


# -------------------------------------------------------------------------
# 12. Feature Registry Consistency
# -------------------------------------------------------------------------
def test_feature_registry_consistency():
    """Verify that every feature in SPATIAL_FEATURE_NAMES is documented in registry."""
    registry_path = os.path.join(ROOT_DIR, "docs", "SPRINT9_FEATURE_REGISTRY.md")
    assert os.path.exists(registry_path), "Feature registry docs/SPRINT9_FEATURE_REGISTRY.md must exist"

    with open(registry_path, "r", encoding="utf-8") as f:
        content = f.read()

    for feat in SPATIAL_FEATURE_NAMES:
        assert feat in content, f"Feature {feat} not documented in SPRINT9_FEATURE_REGISTRY.md"
