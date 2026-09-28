def test_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data
    assert data["database"] == "connected"
    assert "version" in data


def test_system_info_endpoint(client):
    response = client.get("/api/v1/system/info")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    sys_info = data["data"]
    assert sys_info["app_name"] == "CycloneGuard"
    assert sys_info["research_status"] == "Research & Demonstration Platform"
    assert sys_info["database_connected"] is True
    assert "model_inference_status" in sys_info
    # Verify no secrets are exposed in response
    response_text = response.text.lower()
    assert "password" not in response_text
    assert "jwt_secret" not in response_text
    assert "secret" not in response_text
