def test_cyclones_empty_state_and_honesty(client, user_auth_headers):
    response = client.get("/api/v1/cyclones", headers=user_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["cyclones"] == []
    assert data["data"]["total"] == 0
    assert "No operational cyclone data" in data["data"]["status"]
    assert data["data"]["demonstration_data"] is False


def test_historical_cyclones_endpoint(client, user_auth_headers):
    response = client.get("/api/v1/cyclones/historical", headers=user_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["historical_cyclones"] == []
    assert data["data"]["total"] == 0
    assert "No historical reanalysis database" in data["data"]["status"]


def test_cyclone_forecast_endpoint(client, user_auth_headers):
    response = client.get("/api/v1/cyclones/vortex-test-01/forecast", headers=user_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["cyclone_id"] == "vortex-test-01"
    assert data["data"]["status"] == "unavailable"
    assert data["data"]["horizons"] == []


def test_cyclone_analysis_endpoint(client, user_auth_headers):
    response = client.get("/api/v1/cyclones/vortex-test-01/analysis", headers=user_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["cyclone_id"] == "vortex-test-01"
    assert data["data"]["status"] == "unavailable"
    assert data["data"]["ri_risk"]["state"] == "unavailable"
    assert data["data"]["explanation"]["is_available"] is False


def test_models_status_no_fake_deployed_models(client, user_auth_headers):
    response = client.get("/api/v1/models", headers=user_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    models = data["data"]["models"]
    assert len(models) > 0
    # Scientific honesty verification: All models must show deployed == False
    for m in models:
        assert m["deployed"] is False
        assert "not deployed" in m["status"].lower() or "awaiting" in m["status"].lower()


def test_data_sources_status(client, user_auth_headers):
    response = client.get("/api/v1/data-sources", headers=user_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["connected_count"] == 0
    sources = data["data"]["data_sources"]
    assert len(sources) >= 3
    for s in sources:
        assert "not connected" in s["status"].lower() or "awaiting" in s["status"].lower()


def test_predictions_empty_state(client, user_auth_headers):
    response = client.get("/api/v1/predictions", headers=user_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["predictions"] == []
    assert data["data"]["total"] == 0
    assert "not deployed" in data["data"]["message"].lower()


def test_alerts_empty_state(client, user_auth_headers):
    response = client.get("/api/v1/alerts", headers=user_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["alerts"] == []
    assert data["data"]["total"] == 0
    assert "no active alerts" in data["data"]["message"].lower()


def test_password_change_flow(client, user_auth_headers):
    # Test wrong current password
    fail_res = client.post(
        "/api/v1/users/change-password",
        headers=user_auth_headers,
        json={"current_password": "WrongPassword123!", "new_password": "NewSecretPassword2026!"},
    )
    assert fail_res.status_code == 401

    # Test successful password change
    succ_res = client.post(
        "/api/v1/users/change-password",
        headers=user_auth_headers,
        json={"current_password": "StandardUserPass123!", "new_password": "NewSecretPassword2026!"},
    )
    assert succ_res.status_code == 200
    assert "Password successfully updated" in succ_res.json()["data"]["message"]

    # Revert password back so subsequent tests don't fail
    revert_res = client.post(
        "/api/v1/users/change-password",
        headers=user_auth_headers,
        json={"current_password": "NewSecretPassword2026!", "new_password": "StandardUserPass123!"},
    )
    assert revert_res.status_code == 200
