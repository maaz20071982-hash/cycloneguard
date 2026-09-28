def test_register_user_success(client):
    payload = {
        "name": "Meteorologist Alice",
        "email": "alice@meteo.gov",
        "password": "StrongPassword2026!",
        "role": "USER",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    user = data["data"]
    assert user["name"] == "Meteorologist Alice"
    assert user["email"] == "alice@meteo.gov"
    assert user["role"] == "USER"
    assert "password_hash" not in user
    assert "password" not in user


def test_register_duplicate_email(client, test_user):
    payload = {
        "name": "Another User",
        "email": test_user.email,  # Existing email
        "password": "AnotherPassword123!",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "RESOURCE_CONFLICT"


def test_register_short_password(client):
    payload = {
        "name": "Short Pass User",
        "email": "short@test.org",
        "password": "short",  # Less than 8 chars
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_FAILED"


def test_login_success(client, test_user):
    payload = {
        "email": test_user.email,
        "password": "StandardUserPass123!",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    login_data = data["data"]
    assert "access_token" in login_data
    assert login_data["token_type"] == "bearer"
    assert login_data["user"]["email"] == test_user.email


def test_login_invalid_password(client, test_user):
    payload = {
        "email": test_user.email,
        "password": "IncorrectPassword999!",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "AUTHENTICATION_FAILED"


def test_login_nonexistent_user(client):
    payload = {
        "email": "unknown_officer@meteo.gov",
        "password": "SomePassword123!",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "AUTHENTICATION_FAILED"


def test_get_current_user_me(client, test_user, user_auth_headers):
    response = client.get("/api/v1/auth/me", headers=user_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    user = data["data"]
    assert user["id"] == test_user.id
    assert user["email"] == test_user.email
    assert user["role"] == "USER"


def test_get_current_user_unauthorized(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "AUTHENTICATION_FAILED"


def test_get_current_user_invalid_token(client):
    response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid.jwt.token"})
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "AUTHENTICATION_FAILED"
