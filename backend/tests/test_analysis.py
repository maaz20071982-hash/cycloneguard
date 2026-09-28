"""
Integration and unit tests for CycloneGuard AI Analysis and Baseline Model Endpoints.
Verifies Phase 23 & 24 of Sprint 5:
- POST /api/v1/analysis/cyclone
- GET /api/v1/admin/models/baseline
- Scientific honesty: forecast reported as Uninitialized, no fake predictions
"""

from fastapi.testclient import TestClient


def test_analysis_endpoint_unauthorized(client: TestClient):
    """Verify endpoint rejects unauthenticated requests."""
    res = client.post(
        "/api/v1/analysis/cyclone",
        json={
            "storm_id": "2023129N08091",
            "storm_name": "MOCHA",
            "latitude": 13.0,
            "longitude": 88.0,
            "wind_speed_kts": 65.0,
        },
    )
    assert res.status_code == 401


def test_analysis_endpoint_authenticated(client: TestClient, user_auth_headers: dict):
    """Verify analysis endpoint returns CycloneState, baseline assessment, and honest forecast status."""
    payload = {
        "storm_id": "2023129N08091",
        "storm_name": "MOCHA",
        "timestamp_utc": "2023-05-11T12:00:00Z",
        "latitude": 13.0,
        "longitude": 88.0,
        "wind_speed_kts": 75.0,
        "central_pressure_mb": 975.0,
    }
    res = client.post("/api/v1/analysis/cyclone", json=payload, headers=user_auth_headers)
    assert res.status_code == 200
    
    data = res.json()["data"]
    assert data["storm_id"] == "2023129N08091"
    assert data["storm_name"] == "MOCHA"
    
    # Verify CycloneState structure
    cstate = data["cyclone_state"]
    assert cstate["storm_id"] == "2023129N08091"
    assert cstate["intensity"]["value"] == 75.0
    assert cstate["intensity"]["unit"] == "knots"
    assert "noaa_ibtracs" in cstate["available_sources"]
    
    # Verify Baseline RI assessment
    ri = data["ri_baseline_assessment"]
    assert ri is not None
    assert ri["model_version"] == "v1.0.0-baseline"
    assert 0.0 <= ri["ri_probability"] <= 1.0
    assert ri["risk_tier"] in ["ELEVATED_RISK", "LOW_RISK"]
    assert "WMO / NHC" in ri["scientific_standard"]
    
    # Verify Scientific Honesty for forecast
    forecast = data["forecast"]
    assert forecast["status"] == "Uninitialized"
    assert "future development sprints" in forecast["message"]
    
    # Verify Explanation attribution
    explanation = data["explanation"]
    assert explanation is not None
    assert explanation["method"] == "linear_feature_attribution"
    assert "disclaimer" in explanation


def test_admin_baseline_model_metadata(client: TestClient, admin_auth_headers: dict):
    """Verify admin endpoint exposes verified baseline model metadata."""
    res = client.get("/api/v1/admin/models/baseline", headers=admin_auth_headers)
    assert res.status_code == 200
    
    data = res.json()["data"]
    assert data["status"] == "Evaluated"
    meta = data["model_metadata"]
    assert meta["model_type"] == "logistic_regression"
    assert "2023129N08091" in meta["training_metadata"]["test_storms"]
    assert meta["evaluation_metrics"]["roc_auc"] > 0.5
    assert len(data["feature_schema"]["feature_names"]) > 0


def test_admin_models_list_includes_baseline(client: TestClient, admin_auth_headers: dict):
    """Verify /api/v1/admin/models includes the baseline model block."""
    res = client.get("/api/v1/admin/models", headers=admin_auth_headers)
    assert res.status_code == 200
    data = res.json()["data"]
    
    assert "models" in data
    assert "baseline_model" in data
    assert data["baseline_model"]["model_name"] == "CycloneGuard-Baseline-RI"
    assert data["baseline_model"]["version"] == "v1.0.0"
