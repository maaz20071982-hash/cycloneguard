def test_admin_route_forbidden_for_standard_user(client, user_auth_headers):
    """Standard USER role must be blocked with HTTP 403 from admin-only routes."""
    response = client.get("/api/v1/users", headers=user_auth_headers)
    assert response.status_code == 403
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "FORBIDDEN_ACCESS"


def test_admin_route_allowed_for_admin_user(client, admin_auth_headers, test_user, test_admin):
    """ADMIN role must successfully access user management lists."""
    response = client.get("/api/v1/users", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    users_data = data["data"]
    assert users_data["total"] >= 2
    assert len(users_data["users"]) >= 2
    emails = [u["email"] for u in users_data["users"]]
    assert test_user.email in emails
    assert test_admin.email in emails


def test_admin_route_unauthenticated(client):
    """Accessing admin route without bearer credentials returns HTTP 401."""
    response = client.get("/api/v1/users")
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "AUTHENTICATION_FAILED"


def test_user_can_view_own_profile(client, test_user, user_auth_headers):
    response = client.get(f"/api/v1/users/{test_user.id}", headers=user_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == test_user.email


def test_user_cannot_view_other_user_profile(client, test_user, test_admin, user_auth_headers):
    # test_user attempts to inspect test_admin's private profile
    response = client.get(f"/api/v1/users/{test_admin.id}", headers=user_auth_headers)
    assert response.status_code == 403
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "FORBIDDEN_ACCESS"


def test_admin_can_view_any_user_profile(client, test_user, admin_auth_headers):
    # test_admin inspects test_user's profile
    response = client.get(f"/api/v1/users/{test_user.id}", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == test_user.email
