import pytest
from app.models.user import UserRole


ADMIN_ENDPOINTS = [
    "/api/v1/admin/dashboard",
    "/api/v1/admin/data-sources",
    "/api/v1/admin/models",
    "/api/v1/admin/predictions",
    "/api/v1/admin/alerts",
    "/api/v1/admin/users",
    "/api/v1/admin/audit-logs",
    "/api/v1/admin/system",
]


@pytest.mark.parametrize("endpoint", ADMIN_ENDPOINTS)
def test_unauthenticated_request_to_admin_endpoints(client, endpoint):
    """Unauthenticated requests must be rejected with HTTP 401."""
    response = client.get(endpoint)
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "AUTHENTICATION_FAILED"


@pytest.mark.parametrize("endpoint", ADMIN_ENDPOINTS)
def test_standard_user_forbidden_from_admin_endpoints(client, user_auth_headers, endpoint):
    """Standard USER role must be strictly forbidden with HTTP 403."""
    response = client.get(endpoint, headers=user_auth_headers)
    assert response.status_code == 403
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "FORBIDDEN_ACCESS"


@pytest.mark.parametrize("endpoint", ADMIN_ENDPOINTS)
def test_admin_user_allowed_on_admin_endpoints(client, admin_auth_headers, endpoint):
    """ADMIN role must be allowed access with HTTP 200."""
    response = client.get(endpoint, headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data


def test_admin_dashboard_telemetry_honesty(client, admin_auth_headers):
    """Dashboard must report truthful state without fabricated statistics."""
    response = client.get("/api/v1/admin/dashboard", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]

    # Operational status checks
    assert data["data_sources"]["status"] == "Not connected"
    assert data["data_sources"]["connected"] == 0
    assert data["models"]["status"] == "Not deployed"
    assert data["models"]["deployed"] == 0
    assert data["predictions"]["total"] == 0
    assert data["alerts"]["active"] == 0

    # Separate health checks
    assert data["health"]["application"] == "ok"
    assert data["health"]["database"] in ["connected", "ok"]
    assert data["health"]["ai_engine"] == "not_deployed"
    assert data["health"]["data_pipeline"] == "not_connected"

    # User metrics
    assert data["users"]["total"] >= 1
    assert data["users"]["admins"] >= 1


def test_admin_data_sources_registry(client, admin_auth_headers):
    """Data sources registry must display all potential feeds as not connected."""
    response = client.get("/api/v1/admin/data-sources", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total"] == 6
    assert data["connected_count"] == 0
    sources = data["data_sources"]
    names = [s["name"] for s in sources]
    assert any("IMD" in n for n in names)
    assert any("INSAT" in n for n in names)
    assert any("HURSAT" in n for n in names)
    assert any("IBTrACS" in n for n in names)
    assert any("ASCAT" in n for n in names)
    assert any("SAPHIR" in n for n in names)

    # Verify no fake update timestamps
    for s in sources:
        assert s["last_successful_update"] is None
        assert s["last_failure"] is None
        assert s["records_processed"] is None


def test_admin_models_registry(client, admin_auth_headers):
    """Models registry must reflect all 6 architectures as Not deployed with zero fake metrics."""
    response = client.get("/api/v1/admin/models", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total"] == 6
    assert data["active_deployments"] == 0
    models = data["models"]
    model_names = [m["model_name"] for m in models]
    assert "CycloneNet-Detect" in model_names
    assert "CycloneNet-Classify" in model_names
    assert "CycloneNet-Intensity" in model_names
    assert "CycloneNet-RI" in model_names
    assert "CycloneNet-Forecast" in model_names
    assert "CycloneNet-Explain" in model_names

    for m in models:
        assert m["status"] == "Not deployed"
        assert m["deployed"] is False
        assert m["evaluation"] is None
        assert m["metrics"] is None


def test_admin_predictions_empty_state(client, admin_auth_headers):
    """Predictions endpoint returns honest empty list with prepared columns."""
    response = client.get("/api/v1/admin/predictions", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["predictions"] == []
    assert data["total"] == 0
    assert "columns" in data


def test_admin_alerts_empty_state_and_disclaimer(client, admin_auth_headers):
    """Alerts endpoint returns empty list and clear advisory disclaimer."""
    response = client.get("/api/v1/admin/alerts", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["alerts"] == []
    assert data["total"] == 0
    assert "disclaimer" in data
    assert "evacuation orders" in data["disclaimer"].lower()


def test_admin_user_management_lifecycle(client, admin_auth_headers, test_user, test_admin):
    """Admin can inspect, update role, and activate/deactivate users."""
    # 1. Admin gets single user
    response = client.get(f"/api/v1/admin/users/{test_user.id}", headers=admin_auth_headers)
    assert response.status_code == 200
    assert response.json()["data"]["email"] == test_user.email

    # 2. Admin promotes test_user to ADMIN
    response = client.patch(
        f"/api/v1/admin/users/{test_user.id}",
        json={"role": "ADMIN"},
        headers=admin_auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["data"]["role"] == "ADMIN"

    # 3. Admin demotes test_user back to USER
    response = client.patch(
        f"/api/v1/admin/users/{test_user.id}",
        json={"role": "USER"},
        headers=admin_auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["data"]["role"] == "USER"

    # 4. Admin deactivates test_user
    response = client.patch(
        f"/api/v1/admin/users/{test_user.id}/status",
        json={"is_active": False},
        headers=admin_auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["data"]["is_active"] is False

    # 5. Admin reactivates test_user
    response = client.patch(
        f"/api/v1/admin/users/{test_user.id}/status",
        json={"is_active": True},
        headers=admin_auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["data"]["is_active"] is True


def test_admin_cannot_revoke_own_role(client, admin_auth_headers, test_admin):
    """Admin cannot remove their own ADMIN role (lockout prevention)."""
    response = client.patch(
        f"/api/v1/admin/users/{test_admin.id}",
        json={"role": "USER"},
        headers=admin_auth_headers,
    )
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert "lockout" in data["error"]["message"].lower()


def test_admin_cannot_deactivate_self(client, admin_auth_headers, test_admin):
    """Admin cannot deactivate their own account (lockout prevention)."""
    response = client.patch(
        f"/api/v1/admin/users/{test_admin.id}/status",
        json={"is_active": False},
        headers=admin_auth_headers,
    )
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert "lockout" in data["error"]["message"].lower()


def test_standard_user_cannot_modify_user_role_or_status(client, user_auth_headers, test_user, test_admin):
    """Standard USER cannot modify any user role or status."""
    # Attempt role modification
    response = client.patch(
        f"/api/v1/admin/users/{test_user.id}",
        json={"role": "ADMIN"},
        headers=user_auth_headers,
    )
    assert response.status_code == 403

    # Attempt status modification
    response = client.patch(
        f"/api/v1/admin/users/{test_admin.id}/status",
        json={"is_active": False},
        headers=user_auth_headers,
    )
    assert response.status_code == 403


def test_audit_logging_flow(client, admin_auth_headers, test_user, test_admin):
    """Audit logs must record real events: role change, status change, and admin login."""
    # 1. Perform a role change
    client.patch(
        f"/api/v1/admin/users/{test_user.id}",
        json={"role": "ADMIN"},
        headers=admin_auth_headers,
    )

    # 2. Perform a status change
    client.patch(
        f"/api/v1/admin/users/{test_user.id}/status",
        json={"is_active": False},
        headers=admin_auth_headers,
    )

    # 3. Retrieve audit logs
    response = client.get("/api/v1/admin/audit-logs", headers=admin_auth_headers)
    assert response.status_code == 200
    logs = response.json()["data"]["logs"]
    actions = [l["action"] for l in logs]
    assert "USER_ROLE_CHANGED" in actions
    assert "USER_DEACTIVATED" in actions

    # Verify no passwords or secrets are contained in metadata
    for log in logs:
        meta_str = str(log.get("metadata", "")).lower()
        assert "password" not in meta_str
        assert "secret" not in meta_str
        assert "token" not in meta_str


def test_admin_login_creates_audit_log(client, test_admin, admin_auth_headers):
    """Admin login via /auth/login must record an ADMIN_LOGIN audit log."""
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": test_admin.email, "password": "AdminSecurePass123!"},
    )
    assert login_response.status_code == 200

    # Check audit logs
    response = client.get("/api/v1/admin/audit-logs", headers=admin_auth_headers)
    assert response.status_code == 200
    logs = response.json()["data"]["logs"]
    actions = [l["action"] for l in logs]
    assert "ADMIN_LOGIN" in actions


def test_admin_logout_creates_audit_log(client, admin_auth_headers):
    """Admin session logout must record an ADMIN_LOGOUT audit event."""
    logout_response = client.post("/api/v1/auth/logout", headers=admin_auth_headers)
    assert logout_response.status_code == 200

    response = client.get("/api/v1/admin/audit-logs", headers=admin_auth_headers)
    assert response.status_code == 200
    logs = response.json()["data"]["logs"]
    actions = [l["action"] for l in logs]
    assert "ADMIN_LOGOUT" in actions


def test_admin_system_endpoint_telemetry(client, admin_auth_headers):
    """Admin system endpoint returns configuration and health without credential leakage."""
    response = client.get("/api/v1/admin/system", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["app_name"] == "CycloneGuard"
    assert data["backend"]["status"] == "operational"
    assert data["ai_engine"]["status"] == "not_deployed"
    assert data["data_pipeline"]["status"] == "not_connected"
    assert data["database"]["status"] in ["connected", "ok"]

    # Verify no secrets in response text
    resp_text = response.text.lower()
    assert "password" not in resp_text
    assert "jwt_secret" not in resp_text
    assert "secret" not in resp_text
