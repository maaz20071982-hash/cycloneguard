"""
Tests for CycloneGuard Sprint 11 — Final Multi-Storm Validation & Model Freeze.

Verifies:
1. Reproducibility of Sprint 10 benchmark metrics on Chapala.
2. Strict storm-wise partition isolation.
3. Feature schema integrity: Finalist T (23 features) and Finalist TS (61 features).
4. Strict exclusion of environmental features from finalists.
5. Correct handling of undefined metrics on zero-prevalence cohorts (Helen).
6. Model manifest integrity and loadability of frozen artifacts in models/ri/final/.
7. Error analysis export verification (598 rows, required columns).
"""

import json
import os
import pickle
import numpy as np
import pandas as pd
import pytest

from ml.datasets.environmental_ri_dataset import (
    EnvironmentalRIDatasetBuilder,
    MODEL_T_FEATURES,
    MODEL_TS_FEATURES,
    MODEL_E_FEATURES,
)
from ml.evaluation.run_sprint11_validation import (
    evaluate_predictions,
    run_benchmark_reproducibility,
)


@pytest.fixture(scope="module")
def project_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


@pytest.fixture(scope="module")
def dataset(project_root):
    builder = EnvironmentalRIDatasetBuilder(project_root=project_root)
    return builder.build()


def test_finalist_feature_definitions():
    """Verify feature counts and strict exclusion of environmental features from finalists."""
    assert len(MODEL_T_FEATURES) == 23, "Finalist T must have exactly 23 temporal features"
    assert len(MODEL_TS_FEATURES) == 61, "Finalist TS must have exactly 61 features (23 temporal + 38 spatial)"

    # Strict exclusion check: No environmental feature in finalists
    for env_feat in MODEL_E_FEATURES:
        assert env_feat not in MODEL_T_FEATURES, f"Environmental feature {env_feat} found in Finalist T"
        assert env_feat not in MODEL_TS_FEATURES, f"Environmental feature {env_feat} found in Finalist TS"


def test_storm_wise_isolation(dataset):
    """Verify that observations belong to mutually exclusive storm lifecycles."""
    storms = set(s.storm_name for s in dataset.samples)
    assert len(storms) == 6, f"Expected 6 historical storms, found {len(storms)}"
    expected_storms = {"PHAILIN", "HELEN", "HUDHUD", "NILOFAR", "MEGH", "CHAPALA"}
    assert storms == expected_storms, f"Storm set mismatch: {storms} vs {expected_storms}"

    # Partition isolation
    train_storms = set(s.storm_name for s in dataset.filter_by_partition("TRAIN").samples)
    val_storms = set(s.storm_name for s in dataset.filter_by_partition("VAL").samples)
    test_storms = set(s.storm_name for s in dataset.filter_by_partition("TEST").samples)

    assert train_storms.isdisjoint(val_storms), "Train and Val partitions share storm lifecycles!"
    assert train_storms.isdisjoint(test_storms), "Train and Test partitions share storm lifecycles!"
    assert val_storms.isdisjoint(test_storms), "Val and Test partitions share storm lifecycles!"


def test_benchmark_reproducibility(dataset):
    """Verify that benchmark models reproduce reference metrics on Chapala."""
    res_t = run_benchmark_reproducibility(dataset, list(MODEL_T_FEATURES))
    res_ts = run_benchmark_reproducibility(dataset, list(MODEL_TS_FEATURES))

    # Model T
    m_t = res_t["test_metrics"]
    assert pytest.approx(m_t["roc_auc"], abs=0.01) == 0.8279
    assert pytest.approx(m_t["pr_auc"], abs=0.01) == 0.4011
    assert pytest.approx(m_t["recall"], abs=0.01) == 0.9000
    assert m_t["confusion_matrix"]["fp"] == 10
    assert m_t["confusion_matrix"]["fn"] == 1

    # Model TS
    m_ts = res_ts["test_metrics"]
    assert pytest.approx(m_ts["roc_auc"], abs=0.01) == 0.7349
    assert pytest.approx(m_ts["pr_auc"], abs=0.01) == 0.6109
    assert pytest.approx(m_ts["precision"], abs=0.01) == 1.0000
    assert m_ts["confusion_matrix"]["fp"] == 0


def test_undefined_metric_handling():
    """Verify that cohorts with 0 positive events return None for ROC-AUC and PR-AUC."""
    y_single_class = np.zeros(30, dtype=int)
    probs = np.random.uniform(0.1, 0.4, 30)

    metrics = evaluate_predictions(y_single_class, probs, threshold=0.25)
    assert metrics["roc_auc"] is None, "ROC-AUC must be None when only one class is present"
    assert metrics["pr_auc"] is None, "PR-AUC must be None when only one class is present"
    assert metrics["accuracy"] >= 0.0
    assert metrics["brier_score"] >= 0.0


def test_final_frozen_model_manifest(project_root):
    """Verify integrity of models/ri/final/model_manifest.json."""
    manifest_path = os.path.join(project_root, "models", "ri", "final", "model_manifest.json")
    assert os.path.exists(manifest_path), f"Frozen manifest not found at {manifest_path}"

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert manifest["model_version"] == "v3.0.0-frozen"
    assert manifest["feature_count"] == 61
    assert manifest["operating_decision_threshold"] == 0.125
    assert len(manifest["feature_list"]) == 61
    assert manifest["training_cohort"]["sample_count"] == 204
    assert manifest["untouched_test_cohort"]["storm"] == "CHAPALA (2015, Arabian Sea)"
    assert "known_limitations" in manifest
    assert len(manifest["known_limitations"]) >= 3


def test_frozen_artifacts_loadable(project_root):
    """Verify that serialized model binary, scaler, and imputer can be loaded and executed."""
    final_dir = os.path.join(project_root, "models", "ri", "final")
    model_path = os.path.join(final_dir, "model.pkl")
    scaler_path = os.path.join(final_dir, "scaler.pkl")
    imputer_path = os.path.join(final_dir, "imputer.pkl")
    schema_path = os.path.join(final_dir, "feature_schema.json")

    assert os.path.exists(model_path)
    assert os.path.exists(scaler_path)
    assert os.path.exists(imputer_path)
    assert os.path.exists(schema_path)

    with open(model_path, "rb") as f:
        model = pickle.load(f)
    with open(scaler_path, "rb") as f:
        scaler = pickle.load(f)
    with open(imputer_path, "rb") as f:
        imputer = pickle.load(f)
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    assert schema["total_features"] == 61

    # Test dummy inference vector with a NaN value to verify imputer and scaler
    dummy_input = np.ones((1, 61), dtype=float)
    dummy_input[0, 10] = np.nan

    imp_val = imputer.transform(dummy_input)
    assert not np.isnan(imp_val).any(), "Imputer failed to resolve NaN"

    scl_val = scaler.transform(imp_val)
    prob = model.predict_proba(scl_val)[0, 1]
    assert 0.0 <= prob <= 1.0, f"Predicted probability {prob} out of valid range [0, 1]"


def test_error_analysis_file_integrity(project_root):
    """Verify data/reports/sprint11_error_analysis.csv exists, has 598 rows, and required columns."""
    err_path = os.path.join(project_root, "data", "reports", "sprint11_error_analysis.csv")
    assert os.path.exists(err_path), f"Error analysis file not found at {err_path}"

    df = pd.read_csv(err_path)
    assert len(df) == 598, f"Expected 598 error records (299 samples * 2 models), found {len(df)}"

    required_cols = [
        "storm_id", "storm_name", "cyclone_time_utc", "ri_target",
        "prediction", "predicted_probability", "error_type", "model",
        "top_available_features", "satellite_availability", "notes"
    ]
    for col in required_cols:
        assert col in df.columns, f"Missing required column: {col}"


def test_scientific_figures_exist(project_root):
    """Verify that all 9 required Sprint 11 publication SVGs exist."""
    fig_dir = os.path.join(project_root, "reports", "figures", "sprint11")
    required_figs = [
        "per_storm_roc_comparison.svg",
        "per_storm_pr_comparison.svg",
        "per_storm_f1_comparison.svg",
        "per_storm_recall_comparison.svg",
        "per_storm_precision_comparison.svg",
        "false_positive_comparison.svg",
        "threshold_sensitivity.svg",
        "feature_importance_stability.svg",
        "calibration_reliability.svg",
    ]
    for fig in required_figs:
        p = os.path.join(fig_dir, fig)
        assert os.path.exists(p), f"Missing required figure: {p}"
        assert os.path.getsize(p) > 500, f"Figure {fig} is unusually small or empty"
