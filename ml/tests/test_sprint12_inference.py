"""
Sprint 12 Machine Learning Tests: Frozen Model Loader & Inference Feature Contract.

Tests:
1. Frozen model loads from models/ri/final/
2. Model version verified as v3.0.0-frozen
3. Feature count verified = 61
4. Feature ordering matches feature_schema.json
5. Valid inference succeeds deterministically
6. Missing features fail feature contract validation
7. Strict rejection of environmental features (env_*)
8. Missing satellite evidence handled via explicit missingness indicators & train-median imputer
9. No silent zero-filling of missing scientific variables
10. Failure to load raises FrozenModelLoadError without falling back to older models
"""

import os
import json
import pytest
import numpy as np
import pandas as pd

from ml.inference.frozen_model import FrozenModelLoader, FrozenModelLoadError
from ml.inference.feature_contract import (
    InferenceFeatureContract,
    FeatureContractValidationError,
    EnvironmentalFeatureForbiddenError,
)


def test_frozen_model_loads_successfully():
    """Verify frozen model, scaler, and imputer load strictly from models/ri/final/."""
    loader = FrozenModelLoader()
    assert loader.is_loaded is True
    assert loader.model_version == "v3.0.0-frozen"
    assert loader.feature_count == 61
    assert len(loader.feature_names) == 61


def test_model_manifest_validation():
    """Verify model manifest integrity and certification status."""
    loader = FrozenModelLoader()
    manifest = loader.manifest
    assert manifest.get("model_version") == "v3.0.0-frozen"
    assert manifest.get("model_name") == "CycloneGuard-RI-Multimodal-TS-Final"
    assert manifest.get("operating_decision_threshold") == 0.125
    assert manifest.get("multi_storm_loso_summary", {}).get("evaluation_storms_count") == 6
    assert "CHAPALA" in manifest.get("untouched_test_cohort", {}).get("storm", "")
    assert "Uncalibrated" in manifest.get("calibration_status", "")


def test_feature_count_and_ordering():
    """Verify feature ordering exactly matches feature_schema.json."""
    loader = FrozenModelLoader()
    schema_path = os.path.join(loader.artifact_dir, "feature_schema.json")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    expected_features = schema["feature_names"]
    assert len(expected_features) == 61
    assert loader.feature_names == expected_features

    # Check temporal vs spatial breakdown
    temporal_count = sum(1 for f in loader.feature_names if f in InferenceFeatureContract.temporal_features)
    assert temporal_count == 23
    assert len(loader.feature_names) - temporal_count == 38


def test_feature_contract_valid_dataframe():
    """Test feature contract accepts a complete, correctly ordered 61-feature DataFrame."""
    contract = InferenceFeatureContract()
    dummy_dict = {feat: [0.0] for feat in contract.feature_names}
    df = pd.DataFrame(dummy_dict)
    validated = contract.validate_dataframe(df)
    assert validated.shape == (1, 61)
    assert list(validated.columns) == contract.feature_names


def test_feature_contract_missing_features_fails():
    """Test feature contract rejects DataFrames with missing features."""
    contract = InferenceFeatureContract()
    # Missing features
    df = pd.DataFrame({contract.feature_names[0]: [1.0]})
    with pytest.raises(FeatureContractValidationError) as exc:
        contract.validate_dataframe(df)
    assert "Missing 60 required features" in str(exc.value)


def test_strict_rejection_of_environmental_features():
    """Sprint 10 ablation proved environmental fusion lacks incremental signal.

    Verify that submitting any env_* feature raises EnvironmentalFeatureForbiddenError.
    """
    contract = InferenceFeatureContract()
    features = {feat: 0.0 for feat in contract.feature_names}
    features["env_vertical_wind_shear_kts"] = 12.5

    with pytest.raises(EnvironmentalFeatureForbiddenError) as exc:
        contract.validate_observation_features(features)
    assert "Environmental features are strictly excluded from the frozen production model" in str(exc.value)


def test_no_silent_zero_filling_and_explicit_satellite_missingness():
    """Missing satellite features must use explicit indicators (has_irwvp=0.0, has_vschn=0.0)

    and np.nan for unobserved channel fields (to be imputed by train median), NOT arbitrary 0.0.
    """
    contract = InferenceFeatureContract()
    # Case: only temporal features provided
    features_temporal_only = {
        feat: 1.0 for feat in contract.temporal_features
    }
    # Preprocess
    full_vector = contract.preprocess_features(features_temporal_only, allow_missing_spatial=True)
    assert len(full_vector) == 61
    assert full_vector["has_irwvp"] == 0.0
    assert full_vector["has_vschn"] == 0.0
    assert np.isnan(full_vector["irwin_core_mean"])
    assert np.isnan(full_vector["ir_wv_diff_mean"])


def test_frozen_inference_deterministic_score():
    """Test deterministic scoring on verified historical feature values."""
    loader = FrozenModelLoader()
    from ml.datasets.spatial_ri_dataset import SpatialRIDatasetBuilder
    builder = SpatialRIDatasetBuilder()
    dataset = builder.build()
    chapala_samples = [s for s in dataset.samples if "CHAPALA" in s.storm_name]
    assert len(chapala_samples) > 0

    first_sample = chapala_samples[0]
    feature_dict = InferenceFeatureContract.assemble_contract_vector(
        temporal_dict=first_sample.temporal_features,
        spatial_dict=first_sample.spatial_features,
    )

    score, attrib = loader.predict_single(feature_dict)
    assert 0.0 <= score <= 1.0
    assert isinstance(attrib, dict)
    assert "top_supporting" in attrib
    assert "top_suppressing" in attrib

    # Test exact deterministic reproducibility
    score2, _ = loader.predict_single(feature_dict)
    assert score == score2


def test_frozen_loader_fails_loudly_without_fallback(tmp_path):
    """If frozen model directory is invalid, it must raise FrozenModelLoadError

    and NEVER fall back to legacy v1/v2 models.
    """
    empty_dir = str(tmp_path / "empty_models")
    os.makedirs(empty_dir, exist_ok=True)
    with pytest.raises(FrozenModelLoadError) as exc:
        FrozenModelLoader(artifact_dir=empty_dir)
    assert "Frozen model directory not found" in str(exc.value) or "Required frozen artifact" in str(exc.value)
