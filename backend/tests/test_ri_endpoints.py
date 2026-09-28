"""
Backend API Tests for Sprint 6 Rapid Intensification (RI) Endpoints:
- GET /api/v1/models/ri
- POST /api/v1/predictions/ri
- GET /api/v1/cyclones/{storm_id}/ri-risk
- GET /api/v1/predictions/ri/{storm_id}
- GET /api/v1/admin/models/ri
"""

import pytest


def test_get_ri_model_metadata_unauthorized(client):
    """Unauthenticated call to /api/v1/models/ri must be rejected with 401."""
    res = client.get("/api/v1/models/ri")
    assert res.status_code == 401
    assert res.json()["success"] is False


def test_get_ri_model_metadata_authorized(client, user_auth_headers):
    """Authenticated user can inspect model metadata and evaluation metrics."""
    res = client.get("/api/v1/models/ri", headers=user_auth_headers)
    assert res.status_code == 200
    data = res.json()["data"]

    assert data["status"] == "Evaluated"
    assert "version" in data
    assert data["version"] == "v1.0.0"
    assert data["target_horizon"] == "24 hours"
    assert "Delta V >= 30 kts" in data["ri_threshold"]
    assert "test_metrics" in data
    assert data["test_metrics"]["f1"] > 0
    assert len(data["scientific_limitations"]) >= 3


def test_predict_ri_risk_unauthorized(client):
    """Unauthenticated call to /api/v1/predictions/ri must be rejected with 401."""
    payload = {
        "storm_id": "TEST_001",
        "latitude": 12.5,
        "longitude": 84.0,
        "wind_speed_kts": 50.0,
    }
    res = client.post("/api/v1/predictions/ri", json=payload)
    assert res.status_code == 401


def test_predict_ri_risk_valid(client, user_auth_headers):
    """Generate Rapid Intensification prediction from valid observation."""
    payload = {
        "storm_id": "TEST_001",
        "storm_name": "TEST_STORM",
        "observation_time_utc": "2023-05-12T12:00:00Z",
        "latitude": 13.0,
        "longitude": 85.0,
        "wind_speed_kts": 65.0,
        "central_pressure_mb": 980.0,
        "prev_wind_speed_kts": 45.0,
        "prev_latitude": 12.0,
        "prev_longitude": 84.5,
        "prev_time_utc": "2023-05-12T06:00:00Z",
    }
    res = client.post("/api/v1/predictions/ri", json=payload, headers=user_auth_headers)
    assert res.status_code == 200
    data = res.json()["data"]

    assert data["storm_id"] == "TEST_001"
    assert data["forecast_horizon_hours"] == 24.0
    assert 0.0 <= data["ri_probability"] <= 1.0
    assert data["risk_tier"] in ["ELEVATED_RISK", "LOW_RISK"]
    assert "Uncalibrated Model Score" in data["score_interpretation"]
    assert isinstance(data["ri_flag"], bool)
    assert "contributing_features" in data
    assert len(data["limitations"]) > 0


def test_predict_ri_risk_missing_optional_sensors(client, user_auth_headers):
    """Engine must not crash when optional previous observation and satellite crops are omitted."""
    payload = {
        "storm_id": "TEST_MINIMAL",
        "latitude": 14.0,
        "longitude": 86.0,
        "wind_speed_kts": 55.0,
    }
    res = client.post("/api/v1/predictions/ri", json=payload, headers=user_auth_headers)
    assert res.status_code == 200
    data = res.json()["data"]

    assert data["storm_id"] == "TEST_MINIMAL"
    assert data["ri_probability"] is not None
    assert any("infrared satellite imagery is absent" in lim.lower() for lim in data["limitations"])


def test_predict_ri_risk_malformed_input(client, user_auth_headers):
    """Pydantic validation must reject invalid coordinates or negative wind speed with 422."""
    payload = {
        "storm_id": "TEST_INVALID",
        "latitude": 999.0,  # Invalid latitude (> 90)
        "longitude": 85.0,
        "wind_speed_kts": -10.0,  # Invalid wind speed (< 0)
    }
    res = client.post("/api/v1/predictions/ri", json=payload, headers=user_auth_headers)
    assert res.status_code == 422


def test_storm_ri_risk_lookup_mocha(client, user_auth_headers):
    """Lookup real RI prediction for held-out test storm Cyclone Mocha."""
    res = client.get("/api/v1/cyclones/mocha/ri-risk", headers=user_auth_headers)
    assert res.status_code == 200
    data = res.json()["data"]

    assert data["status"] == "evaluated"
    assert "MOCHA" in data["storm_name"].upper()
    assessment = data["ri_assessment"]
    assert assessment is not None
    assert assessment["forecast_horizon_hours"] == 24.0
    assert 0.0 <= assessment["ri_probability"] <= 1.0


def test_storm_ri_risk_lookup_nonexistent(client, user_auth_headers):
    """Querying a non-existent cyclone returns truthful unavailable status."""
    res = client.get("/api/v1/cyclones/nonexistent_cyclone_xyz/ri-risk", headers=user_auth_headers)
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["status"] == "unavailable"
    assert data["ri_assessment"] is None


def test_admin_ri_model_endpoint_forbidden_for_user(client, user_auth_headers):
    """Standard user must be forbidden from administrative RI model inspection endpoint."""
    res = client.get("/api/v1/admin/models/ri", headers=user_auth_headers)
    assert res.status_code == 403


def test_admin_ri_model_endpoint_allowed_for_admin(client, admin_auth_headers):
    """Administrator can retrieve complete verified model artifact metadata and feature schema."""
    res = client.get("/api/v1/admin/models/ri", headers=admin_auth_headers)
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["status"] == "Evaluated & Deployed"
    assert "model_metadata" in data
    assert "feature_schema" in data
    assert len(data["feature_schema"]["selected_feature_names"]) == 23
