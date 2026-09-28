"""
Unit tests for CycloneState representation, encoder, scaler, and baseline models.
Verifies Phase 8 to 22 of Sprint 5:
- CycloneState schema
- State vector encoder (reproducible ordering, dual value/flag)
- Train-only feature scaler (no leakage, preservation of indicator flags)
- Storm-wise split verification (assert disjoint)
- Baseline classifier training & evaluation
- Permutation explainability
"""

import json
import os
import tempfile
import numpy as np
import pytest

from ml.data.schemas.track import CycloneTrackPoint, CycloneTrackSeries
from ml.features.cyclone_state import CycloneStateBuilder, CycloneState
from ml.features.state_encoder import CycloneStateEncoder
from ml.features.scaler import CycloneFeatureScaler
from ml.models.baseline import CycloneBaselineClassifier
from ml.explainability.permutation import PermutationExplainer
from ml.data.splitting.storm_split import StormWiseSplitter


def test_cyclone_state_creation_and_serialization():
    """Verify CycloneState creates inspectable schema with physical units."""
    pt = CycloneTrackPoint(
        storm_id="2023129N08091",
        storm_name="MOCHA",
        season=2023,
        basin="NI",
        timestamp_utc="2023-05-11T12:00:00Z",
        latitude=12.5,
        longitude=87.8,
        wind_speed_kts=65.0,
        central_pressure_mb=982.0,
    )

    state = CycloneStateBuilder.build_state(current_track=pt)
    assert isinstance(state, CycloneState)
    assert state.storm_id == "2023129N08091"
    assert state.intensity.value == 65.0
    assert state.intensity.unit == "knots"
    assert state.intensity.source == "noaa_ibtracs"
    assert "noaa_ibtracs" in state.available_sources
    assert state.morphology_features.get("morph_eye_detected") is False

    # Test serialization to JSON
    state_json = state.model_dump_json()
    assert "2023129N08091" in state_json
    reloaded = CycloneState.model_validate_json(state_json)
    assert reloaded.storm_id == state.storm_id
    assert reloaded.intensity.value == state.intensity.value


def test_state_encoder_determinism_and_dual_encoding():
    """Verify state vector encoder produces fixed schema with value and observation flag."""
    pt = CycloneTrackPoint(
        storm_id="2023129N08091",
        storm_name="MOCHA",
        season=2023,
        basin="NI",
        timestamp_utc="2023-05-11T12:00:00Z",
        latitude=12.5,
        longitude=87.8,
        wind_speed_kts=65.0,
        central_pressure_mb=982.0,
    )
    state = CycloneStateBuilder.build_state(current_track=pt)
    encoder = CycloneStateEncoder()
    
    vec1 = encoder.encode(state)
    vec2 = encoder.encode(state)
    
    # Check shape
    assert vec1.shape == (69,)
    # Check deterministic reproducibility
    np.testing.assert_array_equal(vec1, vec2)
    
    # Check that observed wind speed has value and flag=1
    names = encoder.feature_names
    wind_idx = names.index("track_wind_speed_val")
    wind_obs_idx = names.index("track_wind_speed_is_observed")
    assert vec1[wind_idx] == 65.0
    assert vec1[wind_obs_idx] == 1.0
    
    # Check that unobserved satellite feature has value=0.0 and flag=0.0
    eye_idx = names.index("sat_ir_min_temp_val")
    eye_obs_idx = names.index("sat_ir_min_temp_is_observed")
    assert vec1[eye_idx] == 0.0
    assert vec1[eye_obs_idx] == 0.0


def test_scaler_train_only_fit_and_flag_preservation():
    """Verify scaler fits on training data and does not distort binary indicator columns."""
    encoder = CycloneStateEncoder()
    names = encoder.feature_names
    
    # Create fake training matrix (N=10, D=69)
    np.random.seed(42)
    X_train = np.random.randn(10, 69)
    # Set indicator columns strictly to 0.0 and 1.0
    for idx, name in enumerate(names):
        if name.endswith("_is_observed") or name.startswith("quality_"):
            X_train[:, idx] = np.random.choice([0.0, 1.0], size=10)

    scaler = CycloneFeatureScaler(method="standard")
    scaler.fit(X_train, feature_names=names)
    
    X_train_scaled = scaler.transform(X_train)
    
    # Verify indicator columns were NOT modified
    for idx, name in enumerate(names):
        if name.endswith("_is_observed"):
            np.testing.assert_array_equal(X_train[:, idx], X_train_scaled[:, idx])

    # Save and reload scaler
    with tempfile.TemporaryDirectory() as tmpdir:
        spath = os.path.join(tmpdir, "scaler.json")
        scaler.save_json(spath)
        loaded_scaler = CycloneFeatureScaler.load_json(spath)
        X_loaded_scaled = loaded_scaler.transform(X_train)
        np.testing.assert_allclose(X_train_scaled, X_loaded_scaled)


def test_zero_leakage_storm_wise_split():
    """Verify strict disjointness of train, validation, and test storm IDs."""
    storm_ids = [
        "2023129N08091",  # Mocha
        "2023293N10064",  # Tej
        "2023294N14088",  # Hamoon
        "2023319N15087",  # Midhili
        "2023334N05089",  # Michaung
        "2023157N12067",  # Biparjoy
        "2023208N18089",  # One
        "2023273N17070",  # Two
        "2023293N19086",  # Three
        "2023304N18088",  # Four
    ]
    storms_dict = {}
    for sid in storm_ids:
        storms_dict[sid] = CycloneTrackSeries(
            storm_id=sid,
            storm_name="NAME",
            season=2023,
            basin="NI",
            points=[
                CycloneTrackPoint(
                    storm_id=sid,
                    storm_name="NAME",
                    season=2023,
                    basin="NI",
                    timestamp_utc="2023-05-10T00:00:00Z",
                    latitude=10.0,
                    longitude=85.0,
                    wind_speed_kts=35.0,
                )
            ]
        )

    train_dict, val_dict, test_dict, summary = StormWiseSplitter.split_by_ratio(
        storms_dict, train_ratio=0.70, val_ratio=0.15, test_ratio=0.15, seed=42
    )

    train_ids = set(train_dict.keys())
    val_ids = set(val_dict.keys())
    test_ids = set(test_dict.keys())

    # Mandatory zero-leakage assertions
    assert train_ids.isdisjoint(val_ids), "Train and Val storm IDs must be disjoint"
    assert train_ids.isdisjoint(test_ids), "Train and Test storm IDs must be disjoint"
    assert val_ids.isdisjoint(test_ids), "Val and Test storm IDs must be disjoint"
    assert len(train_ids) + len(val_ids) + len(test_ids) == len(storm_ids)


def test_baseline_classifier_fit_and_evaluation():
    """Verify baseline logistic classifier training, probability prediction, and metrics."""
    np.random.seed(42)
    feature_names = [f"feat_{i}" for i in range(10)]
    X = np.random.randn(50, 10)
    # Binary labels with 20% positives
    y = np.zeros(50, dtype=int)
    y[:10] = 1
    
    clf = CycloneBaselineClassifier(model_type="logistic_regression", feature_subset="full")
    clf.fit(X, y, all_feature_names=feature_names)
    
    probs = clf.predict_proba(X)
    assert probs.shape == (50, 2)
    assert np.all(probs >= 0.0) and np.all(probs <= 1.0)
    
    metrics = clf.evaluate(X, y)
    assert 0.0 <= metrics.accuracy <= 1.0
    assert 0.0 <= metrics.precision <= 1.0
    assert 0.0 <= metrics.recall <= 1.0
    assert 0.0 <= metrics.f1 <= 1.0
    assert "tn" in metrics.confusion_matrix
    assert "tp" in metrics.confusion_matrix
    assert metrics.sample_count == 50
    assert metrics.positive_count == 10


def test_permutation_importance_explainer():
    """Verify permutation explainer computes inspectable importance dict without errors."""
    np.random.seed(42)
    # Feature 0 is strongly correlated with y
    X = np.random.randn(40, 5)
    y = (X[:, 0] > 0.0).astype(int)
    feature_names = [f"feat_{i}" for i in range(5)]
    
    clf = CycloneBaselineClassifier(model_type="logistic_regression", feature_subset="full")
    clf.fit(X, y, all_feature_names=feature_names)
    
    explainer = PermutationExplainer(metric="f1", n_repeats=3, random_state=42)
    result = explainer.explain(clf.model, clf.scaler.transform(X), y, feature_names=feature_names)
    
    assert isinstance(result.importance_scores, dict)
    assert len(result.importance_scores) == 5
    assert "feat_0" in result.importance_scores
    assert result.importance_scores["feat_0"] >= result.importance_scores["feat_4"]
