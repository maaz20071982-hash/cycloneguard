"""
Sprint 10 Test Suite: Environmental Context, Multimodal Dataset, and Ablation.

Verifies:
1. Canonical environmental feature names and schemas
2. Shear vector calculation and unit conversions
3. Missing data behavior (never zero-filling, explicit boolean flags)
4. Temporal directional causality (t_env <= t_obs, max 180 min offset, zero lookahead)
5. Storm-wise partition isolation (disjoint storms across train, val, and test)
6. Multimodal dataset matrix construction (Models T, TS, E, TE, STE)
7. Model E and Model STE artifact loading and inference
8. Ablation results schema and metric bounds
9. Scientific SVG figures generation
"""

import json
import math
import os
import pickle
import numpy as np
import pandas as pd
import pytest

from ml.features.environmental import (
    EnvironmentalFeatureExtractor,
    EnvironmentalObservation,
    ENVIRONMENTAL_FEATURE_NAMES,
)
from ml.datasets.environmental_ri_dataset import (
    EnvironmentalRIDatasetBuilder,
    MODEL_T_FEATURES,
    MODEL_TS_FEATURES,
    MODEL_E_FEATURES,
    MODEL_TE_FEATURES,
    MODEL_STE_FEATURES,
    E1_SST_FEATURE_NAMES,
    E2_SHEAR_FEATURE_NAMES,
    E3_SST_SHEAR_FEATURE_NAMES,
)

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


# -------------------------------------------------------------------------
# 1. Feature Registry & Definitions
# -------------------------------------------------------------------------
def test_environmental_feature_registry():
    """Verify canonical 13 environmental features exist and are correctly named."""
    assert len(ENVIRONMENTAL_FEATURE_NAMES) == 13
    assert "env_sst_celsius" in ENVIRONMENTAL_FEATURE_NAMES
    assert "env_sst_potential_above_26c" in ENVIRONMENTAL_FEATURE_NAMES
    assert "env_sst_is_observed" in ENVIRONMENTAL_FEATURE_NAMES
    assert "env_vws_magnitude_kts" in ENVIRONMENTAL_FEATURE_NAMES
    assert "env_vws_direction_deg" in ENVIRONMENTAL_FEATURE_NAMES
    assert "env_wind_speed_850hpa_kts" in ENVIRONMENTAL_FEATURE_NAMES
    assert "env_wind_speed_200hpa_kts" in ENVIRONMENTAL_FEATURE_NAMES
    assert "env_vws_delta_6h_kts" in ENVIRONMENTAL_FEATURE_NAMES
    assert "env_vws_is_observed" in ENVIRONMENTAL_FEATURE_NAMES
    assert "env_relative_humidity_700hpa" in ENVIRONMENTAL_FEATURE_NAMES
    assert "env_relative_humidity_500hpa" in ENVIRONMENTAL_FEATURE_NAMES
    assert "env_rh_is_observed" in ENVIRONMENTAL_FEATURE_NAMES
    assert "env_dt_minutes" in ENVIRONMENTAL_FEATURE_NAMES


# -------------------------------------------------------------------------
# 2. Shear Vector Calculation Math
# -------------------------------------------------------------------------
def test_shear_calculation_math():
    """Verify 850-200 hPa vertical wind shear vector calculations."""
    # Test case: pure easterly 850 hPa at 36 km/h (10 m/s), westerly 200 hPa at 36 km/h (10 m/s)
    # 850 hPa blowing FROM 90 deg (East), 200 hPa blowing FROM 270 deg (West)
    vws_mag, vws_dir, w850, w200 = EnvironmentalFeatureExtractor.calculate_shear(
        w850_kmh=36.0,
        d850_deg=90.0,
        w200_kmh=36.0,
        d200_deg=270.0,
    )
    assert vws_mag is not None
    assert w850 is not None
    assert w200 is not None
    # 36 km/h = 19.4384 knots
    assert abs(w850 - 19.4384) < 0.1
    assert abs(w200 - 19.4384) < 0.1
    # Vector difference is 20 m/s = 72 km/h = 38.87 knots
    assert abs(vws_mag - 38.876) < 0.2


# -------------------------------------------------------------------------
# 3. Missing Data Behavior (No Zero-Filling)
# -------------------------------------------------------------------------
def test_missing_data_behavior_no_zero_filling():
    """Verify that unobserved fields produce NaNs and observed=0, never silent zero-filling."""
    obs_missing = EnvironmentalObservation(
        wind_speed_850hpa_kmh=None,
        wind_direction_850hpa_deg=None,
        wind_speed_200hpa_kmh=None,
        wind_direction_200hpa_deg=None,
        relative_humidity_700hpa_pct=None,
        relative_humidity_500hpa_pct=None,
        sst_celsius=None,
        dt_minutes=0.0,
    )
    feats = EnvironmentalFeatureExtractor.extract_features(obs_missing)

    assert feats["env_sst_is_observed"] == 0.0
    assert np.isnan(feats["env_sst_celsius"]), "Missing SST must be NaN, never 0.0"
    assert np.isnan(feats["env_sst_potential_above_26c"])

    assert feats["env_vws_is_observed"] == 0.0
    assert np.isnan(feats["env_vws_magnitude_kts"]), "Missing VWS must be NaN, never 0.0"
    assert np.isnan(feats["env_wind_speed_850hpa_kts"])

    assert feats["env_rh_is_observed"] == 0.0
    assert np.isnan(feats["env_relative_humidity_700hpa"])


# -------------------------------------------------------------------------
# 4. Temporal Directional Causality in Extracted Dataset
# -------------------------------------------------------------------------
def test_temporal_directional_causality():
    """Verify t_env <= t_obs across all 347 observations in processed dataset."""
    csv_path = os.path.join(ROOT_DIR, "data", "processed", "environmental_context_v1", "environmental_features.csv")
    assert os.path.exists(csv_path), "Processed environmental CSV must exist"
    df = pd.read_csv(csv_path)

    assert len(df) == 347
    # All offsets must be non-negative (t_env <= t_obs)
    assert (df["env_dt_minutes"] >= 0.0).all(), "Negative offset found (future lookahead violation)!"
    # All offsets must be within 180 min tolerance (6-hourly synoptic window)
    assert (df["env_dt_minutes"] <= 180.0).all(), "Offset exceeds 180 min tolerance!"


# -------------------------------------------------------------------------
# 5. Storm-Wise Isolation
# -------------------------------------------------------------------------
def test_storm_wise_isolation():
    """Verify strict partition isolation with zero storm overlap."""
    csv_path = os.path.join(ROOT_DIR, "data", "processed", "environmental_context_v1", "environmental_features.csv")
    df = pd.read_csv(csv_path)

    train_storms = set(df[df["partition"] == "TRAIN"]["storm_name"].unique())
    val_storms = set(df[df["partition"] == "VAL"]["storm_name"].unique())
    test_storms = set(df[df["partition"] == "TEST"]["storm_name"].unique())

    assert train_storms == {"PHAILIN", "HELEN", "HUDHUD", "NILOFAR"}
    assert val_storms == {"MEGH"}
    assert test_storms == {"CHAPALA"}

    assert train_storms.isdisjoint(val_storms)
    assert train_storms.isdisjoint(test_storms)
    assert val_storms.isdisjoint(test_storms)


# -------------------------------------------------------------------------
# 6. Environmental Dataset Builder & Multimodal Shapes
# -------------------------------------------------------------------------
def test_environmental_dataset_builder():
    """Verify EnvironmentalRIDatasetBuilder builds unified dataset with expected dimensions."""
    builder = EnvironmentalRIDatasetBuilder(project_root=ROOT_DIR)
    dataset = builder.build()

    assert len(dataset) == 347
    sup_samples = dataset.get_supervised_samples()
    assert len(sup_samples) == 299

    # Model T: 23 features
    Xt, yt, _ = dataset.to_numpy(list(MODEL_T_FEATURES), supervised_only=True)
    assert Xt.shape == (299, 23)

    # Model TS: 61 features
    Xts, yts, _ = dataset.to_numpy(list(MODEL_TS_FEATURES), supervised_only=True)
    assert Xts.shape == (299, 61)

    # Model E: 13 features
    Xe, ye, _ = dataset.to_numpy(list(MODEL_E_FEATURES), supervised_only=True)
    assert Xe.shape == (299, 13)

    # Model STE: 74 features
    Xste, yste, _ = dataset.to_numpy(list(MODEL_STE_FEATURES), supervised_only=True)
    assert Xste.shape == (299, 74)


# -------------------------------------------------------------------------
# 7. Model Artifacts & Inference
# -------------------------------------------------------------------------
def test_model_e_and_ste_artifacts_and_inference():
    """Verify exported models, scalers, and imputers exist and execute inference."""
    for model_dir, n_feats in [
        (os.path.join(ROOT_DIR, "models", "ri", "v3_environmental"), 13),
        (os.path.join(ROOT_DIR, "models", "ri", "v3_combined"), 74),
    ]:
        assert os.path.exists(os.path.join(model_dir, "model.pkl"))
        assert os.path.exists(os.path.join(model_dir, "imputer.pkl"))
        assert os.path.exists(os.path.join(model_dir, "scaler.pkl"))
        assert os.path.exists(os.path.join(model_dir, "metadata.json"))

        with open(os.path.join(model_dir, "model.pkl"), "rb") as f:
            model = pickle.load(f)
        with open(os.path.join(model_dir, "imputer.pkl"), "rb") as f:
            imputer = pickle.load(f)
        with open(os.path.join(model_dir, "scaler.pkl"), "rb") as f:
            scaler = pickle.load(f)

        # Test dummy input with NaNs
        dummy = np.full((1, n_feats), np.nan)
        dummy[0, 0] = 28.5
        dummy_imp = imputer.transform(dummy)
        dummy_scl = scaler.transform(dummy_imp)
        prob = model.predict_proba(dummy_scl)[0, 1]
        assert 0.0 <= prob <= 1.0


# -------------------------------------------------------------------------
# 8. Ablation Results Schema & Metric Validation
# -------------------------------------------------------------------------
def test_ablation_results_file():
    """Verify SPRINT10_ABLATION_RESULTS.json exists and metrics conform to expectations."""
    ablation_path = os.path.join(ROOT_DIR, "docs", "SPRINT10_ABLATION_RESULTS.json")
    assert os.path.exists(ablation_path), "Ablation results JSON must exist"

    with open(ablation_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["test_storm"] == "CHAPALA"
    assert data["val_storm"] == "MEGH"
    exps = data["experiments"]

    for exp_name in [
        "Model T (Temporal)",
        "Model TS (Temporal + Spatial)",
        "Model E (Environmental Only)",
        "Model TE (Temporal + Environmental)",
        "Model STE (Full Multimodal Fusion)",
    ]:
        assert exp_name in exps
        tm = exps[exp_name]["test_metrics"]
        assert 0.0 <= tm["accuracy"] <= 1.0
        assert 0.0 <= tm["f1"] <= 1.0
        assert 0.0 <= tm["roc_auc"] <= 1.0
        assert 0.0 <= tm["pr_auc"] <= 1.0


# -------------------------------------------------------------------------
# 9. Scientific Figures Exist
# -------------------------------------------------------------------------
def test_scientific_figures_exist():
    """Verify all 8 scientific figures were generated."""
    fig_dir = os.path.join(ROOT_DIR, "reports", "figures", "sprint10")
    expected_figs = [
        "environmental_coverage_by_storm.svg",
        "sst_vs_vws_ri_distribution.svg",
        "sst_distribution_ri_outcomes.svg",
        "vws_distribution_ri_outcomes.svg",
        "multimodal_roc_comparison.svg",
        "multimodal_pr_comparison.svg",
        "environmental_feature_importance.svg",
        "multimodal_ablation_summary.svg",
    ]
    for fig in expected_figs:
        p = os.path.join(fig_dir, fig)
        assert os.path.exists(p), f"Figure {fig} must exist"
        assert os.path.getsize(p) > 500, f"Figure {fig} must have non-trivial size"
