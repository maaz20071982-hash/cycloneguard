"""
Backend Test Suite for Sprint 9 Admin Model Metadata & Monitoring Endpoints.

Tests:
- GET /api/v1/admin/models (contains spatial_model_s and combined_model_st)
- GET /api/v1/admin/models/spatial (Model S metadata and metrics)
- GET /api/v1/admin/models/combined (Model ST metadata and metrics)
- Proper authorization (admin required, 401 unauth, 403 standard user)
- Documented limitations present and non-empty
"""

import pytest


def test_admin_models_sprint9_metadata(client, admin_auth_headers):
    """GET /admin/models must return Model S and Model ST metadata."""
    response = client.get("/api/v1/admin/models", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]

    # Verify spatial Model S metadata
    assert "spatial_model_s" in data
    spatial = data["spatial_model_s"]
    assert spatial is not None
    assert spatial["model_name"] == "CycloneGuard-RI-Spatial-v2"
    assert spatial["feature_count"] == 38
    assert "CHAPALA" in spatial["test_storm"]
    assert "MEGH" in spatial["validation_storm"]
    assert spatial["test_metrics"]["roc_auc"] is not None
    assert len(spatial["limitations"]) >= 3

    # Verify combined Model ST metadata
    assert "combined_model_st" in data
    combined = data["combined_model_st"]
    assert combined is not None
    assert combined["model_name"] == "CycloneGuard-RI-Combined-v2"
    assert combined["feature_count"] == 61
    assert "CHAPALA" in combined["test_storm"]
    assert "MEGH" in combined["validation_storm"]
    assert combined["test_metrics"]["roc_auc"] is not None
    assert len(combined["limitations"]) >= 3


def test_admin_spatial_model_endpoint(client, admin_auth_headers):
    """GET /admin/models/spatial returns Model S metadata and feature schema."""
    response = client.get("/api/v1/admin/models/spatial", headers=admin_auth_headers)
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    data = res["data"]
    assert data["status"] == "Evaluated"
    assert "model_metadata" in data
    assert "feature_schema" in data
    assert data["model_metadata"]["model_name"] == "CycloneGuard-RI-Spatial-v2"


def test_admin_combined_model_endpoint(client, admin_auth_headers):
    """GET /admin/models/combined returns Model ST metadata and feature schema."""
    response = client.get("/api/v1/admin/models/combined", headers=admin_auth_headers)
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    data = res["data"]
    assert data["status"] == "Evaluated"
    assert "model_metadata" in data
    assert "feature_schema" in data
    assert data["model_metadata"]["model_name"] == "CycloneGuard-RI-Combined-v2"


def test_admin_model_endpoints_security(client, user_auth_headers):
    """Endpoints must reject unauthenticated or non-admin requests."""
    for ep in ["/api/v1/admin/models/spatial", "/api/v1/admin/models/combined"]:
        # Unauthenticated -> 401
        res_unauth = client.get(ep)
        assert res_unauth.status_code == 401

        # Standard user -> 403
        res_user = client.get(ep, headers=user_auth_headers)
        assert res_user.status_code == 403
