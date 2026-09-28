"""
Tests for Sprint 6 Rapid Intensification (RI) Machine Learning Pipeline:
- Dataset construction and strict leakage firewalls
- Model loading, versioning, and feature schema integrity
- Deterministic inference
- Missing satellite source resilience without fabrication
- Decision threshold configurability
"""

import os
import json
import pytest
import numpy as np

from ml.datasets.ri_dataset import RIDatasetBuilder, verify_dataset_partitions_disjoint
from ml.models.ri_baseline import RITaskBaseline, RIMetrics
from ml.inference.ri_predictor import RIPredictor
from ml.data.schemas.track import CycloneTrackPoint, CycloneTrackSeries
from ml.features.cyclone_state import CycloneStateBuilder


@pytest.fixture
def sample_track_series():
    """Create a minimal track series with 24h progression for testing."""
    pts = [
        CycloneTrackPoint(
            storm_id="TEST_STORM_01",
            storm_name="TEST_ALPHA",
            season=2023,
            basin="NI",
            timestamp_utc="2023-05-10T00:00:00Z",
            latitude=10.0,
            longitude=85.0,
            wind_speed_kts=40.0,
            central_pressure_mb=1000.0,
        ),
        CycloneTrackPoint(
            storm_id="TEST_STORM_01",
            storm_name="TEST_ALPHA",
            season=2023,
            basin="NI",
            timestamp_utc="2023-05-10T06:00:00Z",
            latitude=10.5,
            longitude=85.5,
            wind_speed_kts=45.0,
            central_pressure_mb=996.0,
        ),
        CycloneTrackPoint(
            storm_id="TEST_STORM_01",
            storm_name="TEST_ALPHA",
            season=2023,
            basin="NI",
            timestamp_utc="2023-05-10T12:00:00Z",
            latitude=11.0,
            longitude=86.0,
            wind_speed_kts=55.0,
            central_pressure_mb=990.0,
        ),
        CycloneTrackPoint(
            storm_id="TEST_STORM_01",
            storm_name="TEST_ALPHA",
            season=2023,
            basin="NI",
            timestamp_utc="2023-05-11T00:00:00Z",
            latitude=12.0,
            longitude=87.0,
            wind_speed_kts=75.0,  # Delta V = 35 kts in 24h -> Positive RI
            central_pressure_mb=975.0,
        ),
    ]
    return CycloneTrackSeries(storm_id="TEST_STORM_01", storm_name="TEST_ALPHA", season=2023, basin="NI", points=pts)


def test_dataset_leakage_firewalls(sample_track_series):
    """Verify that dataset builder asserts target_time > feature_time strictly."""
    storms = {"TEST_STORM_01": sample_track_series}
    builder = RIDatasetBuilder(forecast_horizon_hours=24.0, ri_threshold_kts=30.0)
    dataset = builder.build_from_storms(storms=storms)

    supervised_items = dataset.get_supervised_items()
    # Must contain exactly 1 point that has a forward 24h observation
    assert len(supervised_items) == 1
    item = supervised_items[0]
    assert item.storm_id == "TEST_STORM_01"
    assert item.ri_target == 1  # 75 - 40 = 35 >= 30 kt
    assert item.delta_intensity_kts == 35.0

    # Strict temporal ordering assertion
    assert item.target_time_utc > item.observation_time_utc


def test_disjoint_storm_partitions_assertion(sample_track_series):
    """Verify that verify_dataset_partitions_disjoint catches partition leakage."""
    storm_a = sample_track_series
    pts_b = [pt.model_copy(update={"storm_id": "TEST_STORM_02", "storm_name": "BETA"}) for pt in storm_a.points]
    storm_b = CycloneTrackSeries(storm_id="TEST_STORM_02", storm_name="BETA", season=2023, basin="NI", points=pts_b)
    pts_c = [pt.model_copy(update={"storm_id": "TEST_STORM_03", "storm_name": "GAMMA"}) for pt in storm_a.points]
    storm_c = CycloneTrackSeries(storm_id="TEST_STORM_03", storm_name="GAMMA", season=2023, basin="NI", points=pts_c)

    builder = RIDatasetBuilder()
    ds_a = builder.build_from_storms({"TEST_STORM_01": storm_a})
    ds_b = builder.build_from_storms({"TEST_STORM_02": storm_b})
    ds_c = builder.build_from_storms({"TEST_STORM_03": storm_c})

    # Disjoint splits pass
    verify_dataset_partitions_disjoint(ds_a, ds_b, ds_c)

    # Overlapping train/test must raise AssertionError
    with pytest.raises(AssertionError, match="Leakage detected"):
        verify_dataset_partitions_disjoint(ds_a, ds_b, ds_a)


def test_model_artifact_loading_and_metadata():
    """Verify that the versioned Model v1 package is valid on disk."""
    predictor = RIPredictor.load_default()
    assert predictor is not None
    assert predictor.metadata.get("version") == "v1.0.0"
    assert "CycloneGuard-RI-v1" in predictor.metadata.get("model_name", "")
    assert len(predictor.selected_feature_names) == 23
    assert predictor.decision_threshold > 0.0


def test_deterministic_inference():
    """Verify that consecutive inference calls on identical inputs yield bitwise identical probabilities."""
    predictor = RIPredictor.load_default()
    
    pt = CycloneTrackPoint(
        storm_id="DETERMINISTIC_TEST",
        storm_name="DETERMINISTIC",
        season=2023,
        basin="NI",
        timestamp_utc="2023-05-12T00:00:00Z",
        latitude=15.0,
        longitude=88.0,
        wind_speed_kts=65.0,
        central_pressure_mb=980.0,
    )

    res1 = predictor.predict_track_point(current_track=pt)
    res2 = predictor.predict_track_point(current_track=pt)

    assert res1["ri_probability"] == res2["ri_probability"]
    assert res1["ri_flag"] == res2["ri_flag"]
    assert res1["risk_tier"] == res2["risk_tier"]


def test_missing_satellite_sources_resilience():
    """Verify that absent satellite sensors (IR/microwave) do not crash the engine or inject synthetic values."""
    predictor = RIPredictor.load_default()

    # Point without satellite crop
    pt = CycloneTrackPoint(
        storm_id="SENSOR_TEST",
        storm_name="SENSOR_STORM",
        season=2023,
        basin="NI",
        timestamp_utc="2023-05-12T06:00:00Z",
        latitude=16.0,
        longitude=89.0,
        wind_speed_kts=50.0,
    )

    res = predictor.predict_track_point(current_track=pt)
    assert "ri_probability" in res
    assert any("microwave" in s.lower() or "hursat" in s.lower() for s in res["missing_sources"])
    assert any("infrared satellite imagery is absent" in lim.lower() for lim in res["limitations"])


def test_threshold_override():
    """Verify operational decision threshold configurability."""
    predictor_default = RIPredictor.load_default()
    predictor_high_th = RIPredictor.load_default(override_threshold=0.99)
    predictor_low_th = RIPredictor.load_default(override_threshold=0.01)

    pt = CycloneTrackPoint(
        storm_id="TH_TEST",
        storm_name="TH_STORM",
        season=2023,
        basin="NI",
        timestamp_utc="2023-05-12T12:00:00Z",
        latitude=16.5,
        longitude=89.5,
        wind_speed_kts=60.0,
    )

    res_high = predictor_high_th.predict_track_point(current_track=pt)
    res_low = predictor_low_th.predict_track_point(current_track=pt)

    assert res_high["decision_threshold"] == 0.99
    assert res_low["decision_threshold"] == 0.01
