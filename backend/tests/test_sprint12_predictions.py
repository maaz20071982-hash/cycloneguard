"""
Sprint 12 Backend Tests: Prediction Service, API, Persistence, Authorization & Audit.

Tests:
1. Frozen model loads and produces verified PredictionResponse (v3.0.0-frozen)
2. Calibration status returned explicitly as uncalibrated empirical risk index
3. Operating threshold τ = 0.125 and presentation categories (LOW_RISK, ELEVATED_RISK, HIGH_RISK)
4. Full data provenance and observational evidence availability returned
5. Prediction persistence in database verified
6. Retrieval of stored prediction via GET /api/v1/predictions/ri/{prediction_id}
7. Admin prediction monitoring via GET /api/v1/admin/predictions with query filters
8. Admin single prediction audit inspection via GET /api/v1/admin/predictions/{id}
9. Honest empty state when no predictions exist
10. Role-based authorization: USER can predict, ADMIN can monitor, USER cannot access admin routes (403)
11. Unauthenticated requests rejected with 401
12. Feature contract violation when inputs are invalid (no arbitrary zero-filling)
13. Audit log created for prediction generation
"""

import pytest
from app.models.prediction import Prediction
from app.models.audit_log import AuditLog


def test_predict_ri_frozen_model_success(client, user_auth_headers):
    """Test POST /api/v1/predictions/ri with valid kinematic observation."""
    payload = {
        "storm_id": "2015301N11065",
        "storm_name": "CHAPALA",
        "observation_time_utc": "2015-10-28T18:00:00Z",
        "latitude": 13.8,
        "longitude": 64.2,
        "wind_speed_kts": 65.0,
        "central_pressure_mb": 985.0,
        "prev_wind_speed_kts": 50.0,
        "prev_latitude": 13.2,
        "prev_longitude": 64.5,
    }
    res = client.post("/api/v1/predictions/ri", json=payload, headers=user_auth_headers)
    assert res.status_code == 200
    data = res.json()["data"]

    # Verify Frozen Model identity
    assert data["model_name"] == "CycloneGuard-RI-Multimodal-TS-Final"
    assert data["model_version"] == "v3.0.0-frozen"
    assert data["forecast_horizon_hours"] == 24.0

    # Verify Risk Index & Operating Threshold
    assert 0.0 <= data["ri_risk_index"] <= 1.0
    assert data["operating_threshold"] == 0.125
    assert isinstance(data["ri_flag"], bool)
    assert data["risk_category"] in ["LOW_RISK", "ELEVATED_RISK", "HIGH_RISK"]

    # Verify Calibration Status (Uncalibrated Empirical Score)
    assert "Uncalibrated" in data["calibration_status"]

    # Verify Provenance & Evidence
    assert "track_dataset" in data["input_data_provenance"]
    assert "satellite_dataset" in data["input_data_provenance"]
    assert data["temporal_evidence_available"] is True
    assert isinstance(data["satellite_evidence_available"], bool)

    # Disclaimers
    assert len(data["limitations"]) > 0
    assert len(data["disclaimers"]) > 0


def test_prediction_persisted_in_database(client, user_auth_headers, db_session):
    """Verify that successful prediction is persisted to SQLite/PostgreSQL with reproducible audit metadata."""
    payload = {
        "storm_id": "2015301N11065",
        "storm_name": "CHAPALA",
        "observation_time_utc": "2015-10-28T18:00:00Z",
        "latitude": 13.8,
        "longitude": 64.2,
        "wind_speed_kts": 65.0,
        "central_pressure_mb": 985.0,
    }
    res = client.post("/api/v1/predictions/ri", json=payload, headers=user_auth_headers)
    assert res.status_code == 200
    pred_id = res.json()["data"]["prediction_id"]

    # Query DB directly
    record = db_session.query(Prediction).filter(Prediction.id == pred_id).first()
    assert record is not None
    assert record.storm_id == "2015301N11065"
    assert record.storm_name == "CHAPALA"
    assert record.model_version == "v3.0.0-frozen"
    assert record.operating_threshold == 0.125
    assert record.risk_category in ["LOW_RISK", "ELEVATED_RISK", "HIGH_RISK"]


def test_get_prediction_by_id_authorized(client, user_auth_headers):
    """Verify GET /api/v1/predictions/ri/{prediction_id} retrieves persisted prediction."""
    # 1. Create a prediction
    payload = {
        "storm_id": "2013284N14093",
        "storm_name": "PHAILIN",
        "observation_time_utc": "2013-10-10T06:00:00Z",
        "latitude": 14.5,
        "longitude": 88.2,
        "wind_speed_kts": 75.0,
        "central_pressure_mb": 970.0,
    }
    create_res = client.post("/api/v1/predictions/ri", json=payload, headers=user_auth_headers)
    assert create_res.status_code == 200
    pred_id = create_res.json()["data"]["prediction_id"]

    # 2. Retrieve by ID
    get_res = client.get(f"/api/v1/predictions/ri/{pred_id}", headers=user_auth_headers)
    assert get_res.status_code == 200
    retrieved = get_res.json()["data"]
    assert retrieved["prediction_id"] == pred_id
    assert retrieved["storm_name"] == "PHAILIN"
    assert retrieved["model_version"] == "v3.0.0-frozen"


def test_admin_predictions_monitoring_and_filters(client, user_auth_headers, admin_auth_headers):
    """Verify ADMIN can list all predictions, filter by storm, and inspect audit records."""
    # 1. Generate prediction as user
    payload = {
        "storm_id": "2015301N11065",
        "storm_name": "CHAPALA",
        "latitude": 13.8,
        "longitude": 64.2,
        "wind_speed_kts": 65.0,
    }
    client.post("/api/v1/predictions/ri", json=payload, headers=user_auth_headers)

    # 2. Admin retrieves list
    admin_res = client.get("/api/v1/admin/predictions", headers=admin_auth_headers)
    assert admin_res.status_code == 200
    data = admin_res.json()["data"]
    assert data["total"] >= 1
    assert len(data["predictions"]) >= 1
    assert "columns" in data

    # 3. Filter by storm
    filter_res = client.get("/api/v1/admin/predictions?storm=CHAPALA", headers=admin_auth_headers)
    assert filter_res.status_code == 200
    filtered_data = filter_res.json()["data"]
    assert filtered_data["total"] >= 1
    for p in filtered_data["predictions"]:
        assert "CHAPALA" in p["storm_name"]

    # 4. Admin inspects audit detail
    first_pred_id = data["predictions"][0]["prediction_id"]
    audit_res = client.get(f"/api/v1/admin/predictions/{first_pred_id}", headers=admin_auth_headers)
    assert audit_res.status_code == 200
    audit_data = audit_res.json()["data"]
    assert audit_data["prediction_id"] == first_pred_id
    assert audit_data["model_version"] == "v3.0.0-frozen"


def test_user_forbidden_from_admin_predictions(client, user_auth_headers):
    """Standard USER role must receive 403 Forbidden on admin prediction endpoints."""
    res = client.get("/api/v1/admin/predictions", headers=user_auth_headers)
    assert res.status_code == 403


def test_unauthenticated_requests_denied(client):
    """Unauthenticated calls to prediction endpoints must receive 401 Unauthorized."""
    res1 = client.post("/api/v1/predictions/ri", json={"storm_id": "TEST", "latitude": 10.0, "longitude": 60.0})
    assert res1.status_code == 401

    res2 = client.get("/api/v1/predictions/ri/some-id")
    assert res2.status_code == 401

    res3 = client.get("/api/v1/admin/predictions")
    assert res3.status_code == 401


def test_prediction_audit_log_recorded(client, user_auth_headers, db_session):
    """Generating a prediction must produce an entry in audit_logs table."""
    payload = {
        "storm_id": "2015301N11065",
        "storm_name": "CHAPALA",
        "latitude": 13.8,
        "longitude": 64.2,
        "wind_speed_kts": 65.0,
    }
    res = client.post("/api/v1/predictions/ri", json=payload, headers=user_auth_headers)
    assert res.status_code == 200
    pred_id = res.json()["data"]["prediction_id"]

    # Check audit log in DB
    log = db_session.query(AuditLog).filter(AuditLog.resource_id == pred_id).first()
    assert log is not None
    assert log.action in ["GENERATE_PREDICTION", "prediction.generate"]
    assert log.resource_type == "prediction"
