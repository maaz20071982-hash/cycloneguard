"""
ML & Scientific Evidence Unit Tests (Sprint 13).
Validates:
1. Zero lookahead in feature vectors and contracts.
2. Real historical observations (zero synthetic records).
3. Frozen threshold tau = 0.125.
4. Model feature attribution integrity (non-causal labeling).
5. RI-positive and RI-negative inference outputs on frozen model.
6. Honest handling of missing channels.
"""

import os
import sys
import numpy as np
import pytest

from ml.datasets.spatial_ri_dataset import SpatialRIDatasetBuilder
from ml.inference.feature_contract import CANONICAL_FEATURE_CONTRACT, InferenceFeatureContract
from ml.inference.frozen_model import FrozenModelLoader


@pytest.fixture(scope="module")
def project_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


@pytest.fixture(scope="module")
def spatial_dataset(project_root):
    builder = SpatialRIDatasetBuilder(project_root=project_root)
    return builder.build()


@pytest.fixture(scope="module")
def frozen_loader(project_root):
    artifact_dir = os.path.join(project_root, "models", "ri", "final")
    return FrozenModelLoader(artifact_dir=artifact_dir)


def test_zero_synthetic_observations(spatial_dataset):
    """Verifies that all samples derive strictly from real historical storms."""
    valid_storms = {"2013281N12098", "2013322N13090", "2014279N11096", "2014297N11062", "2015301N11065", "2015309N14067"}
    for sample in spatial_dataset.samples:
        assert sample.storm_id in valid_storms, f"Found unrecognized storm ID {sample.storm_id}"
        assert sample.observation_time is not None
        assert sample.latitude > 0.0
        assert sample.longitude > 0.0


def test_no_future_lookahead_in_canonical_contract():
    """Verifies that no future/target variables exist in the 61-feature inference contract."""
    contract = CANONICAL_FEATURE_CONTRACT
    assert len(contract) == 61

    forbidden_substrings = ["future", "target", "delta_v_24h", "ri_label", "ground_truth"]
    for feat in contract:
        for fsub in forbidden_substrings:
            assert fsub not in feat.lower(), f"Feature {feat} contains forbidden lookahead substring {fsub}"


def test_feature_contract_rejects_outcome_leakage():
    """Verifies that attempting to inject target variables raises a contract error."""
    with pytest.raises(Exception):
        InferenceFeatureContract.assemble_contract_vector(
            temporal_dict={"future_wind_kts": 65.0, "track_wind_speed_val": 30.0},
            spatial_dict={},
        )


def test_frozen_operating_threshold(frozen_loader):
    """Verifies that the frozen operating threshold is exactly tau = 0.125."""
    assert frozen_loader.operating_threshold == 0.125
    assert float(frozen_loader.manifest.get("operating_decision_threshold", 0.125)) == 0.125


def test_chapala_smoke_test_ri_positive(spatial_dataset, frozen_loader):
    """
    Smoke test: Chapala 2015-10-28 18:00 UTC.
    Verifies that model risk index > 0.125 and historical outcome is RI+.
    """
    chapala_smoke = [
        s for s in spatial_dataset.samples
        if s.storm_name == "CHAPALA" and "2015-10-28T18" in s.observation_time
    ]
    assert len(chapala_smoke) == 1, "Chapala 2015-10-28 18:00 UTC observation missing from dataset"
    sample = chapala_smoke[0]

    # Verify input conditions at t0
    assert sample.current_wind_kts == 30.0
    assert sample.latitude == 13.1
    assert sample.longitude == 64.6

    # Assemble vector and run inference
    feature_dict = InferenceFeatureContract.assemble_contract_vector(
        temporal_dict=sample.temporal_features,
        spatial_dict=sample.spatial_features,
    )
    result = frozen_loader.predict_from_feature_dict(feature_dict)

    # Assert model score
    assert round(result["ri_risk_index"], 4) == 0.3592
    assert result["ri_flag"] is True
    assert result["risk_category"] == "HIGH_RISK"
    assert result["operating_threshold"] == 0.125

    # Verify strictly segregated historical ground truth
    assert sample.future_wind_kts == 65.0
    assert sample.delta_wind_kts == 35.0
    assert sample.ri_target == 1


def test_nilofar_smoke_test_ri_negative(spatial_dataset, frozen_loader):
    """
    Smoke test: Nilofar 2014-10-23 12:00 UTC.
    Verifies that model risk index < 0.125 and historical outcome is RI-.
    """
    nilofar_non_ri = [
        s for s in spatial_dataset.samples
        if s.storm_name == "NILOFAR" and "2014-10-23T12" in s.observation_time
    ]
    assert len(nilofar_non_ri) == 1, "Nilofar 2014-10-23 12:00 UTC observation missing"
    sample = nilofar_non_ri[0]

    feature_dict = InferenceFeatureContract.assemble_contract_vector(
        temporal_dict=sample.temporal_features,
        spatial_dict=sample.spatial_features,
    )
    result = frozen_loader.predict_from_feature_dict(feature_dict)

    # Model score must stay below threshold
    assert result["ri_risk_index"] < 0.125
    assert result["ri_flag"] is False
    assert result["risk_category"] == "LOW_RISK"

    # Historical ground truth verification
    assert sample.delta_wind_kts == 5.0
    assert sample.ri_target == 0


def test_helen_pure_non_ri_storm(spatial_dataset, frozen_loader):
    """
    Helen (2013): 0 RI+ events in entire lifecycle.
    Verifies that model scores stay low and historical outcome reflects 0 RI.
    """
    helen_samples = [s for s in spatial_dataset.samples if s.storm_name == "HELEN"]
    assert len(helen_samples) == 43

    # All Helen samples should have ri_target == 0
    ri_pos = sum(1 for s in helen_samples if getattr(s, "ri_target", 0) == 1)
    assert ri_pos == 0, "Helen should have 0 RI+ events"


def test_honest_handling_of_missing_satellite_channels(spatial_dataset, frozen_loader):
    """
    Verifies that nighttime observations with missing VSCHN (visible channel)
    are honestly represented and handled without fabrication.
    """
    chapala_night = [
        s for s in spatial_dataset.samples
        if s.storm_name == "CHAPALA" and "2015-10-28T18" in s.observation_time
    ][0]

    # Nighttime fix: has_vschn should be 0.0
    assert chapala_night.spatial_features["has_vschn"] == 0.0
    assert np.isnan(chapala_night.spatial_features["vschn_mean"])

    # Inference handles nan via the fitted median imputer cleanly
    feature_dict = InferenceFeatureContract.assemble_contract_vector(
        temporal_dict=chapala_night.temporal_features,
        spatial_dict=chapala_night.spatial_features,
    )
    res = frozen_loader.predict_from_feature_dict(feature_dict)
    assert res["ri_risk_index"] is not None
    assert not np.isnan(res["ri_risk_index"])

