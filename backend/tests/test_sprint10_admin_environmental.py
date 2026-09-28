"""
Backend Test Suite for Sprint 10 Admin Environmental Metadata & Monitoring Endpoints.

Tests:
- GET /api/v1/admin/environmental-coverage (347 observations, 299 supervised, VWS & SST metrics)
- GET /api/v1/admin/models (contains environmental_model_e and multimodal_model_ste)
- GET /api/v1/admin/models/environmental (Model E metadata and metrics)
- GET /api/v1/admin/models/ste (Model STE metadata and metrics)
- GET /api/v1/admin/data-sources (contains NOAA PSL NCEP R2 and OISST v2.0)
- Proper authorization (admin required, 401 unauth)
- Documented limitations present and non-empty
"""

import pytest


def test_admin_environmental_coverage_endpoint(client, admin_auth_headers):
    """GET /admin/environmental-coverage returns real computed environmental coverage statistics."""
    response = client.get("/api/v1/admin/environmental-coverage", headers=admin_auth_headers)
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    data = res["data"]

    assert data["status"] == "Validated & Ingested"
    assert data["total_observations"] == 347
    assert data["supervised_samples"] == 299
    assert data["vws_observed_count"] >= 340
    assert data["vws_coverage_pct"] >= 95.0
    assert data["sst_observed_count"] >= 290
    assert data["sst_coverage_pct"] >= 80.0
    assert data["directional_causality_enforced"] is True
    assert data["future_lookahead_violations"] == 0
    assert len(data["sources"]) == 2
    assert len(data["limitations"]) >= 3
    assert "CHAPALA" in data["storm_breakdown"]
    assert "PHAILIN" in data["storm_breakdown"]


def test_admin_models_sprint10_metadata(client, admin_auth_headers):
    """GET /admin/models must return Model E and Model STE metadata."""
    response = client.get("/api/v1/admin/models", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]

    # Verify environmental Model E metadata
    assert "environmental_model_e" in data
    env_m = data["environmental_model_e"]
    assert env_m is not None
    assert env_m["model_name"] == "CycloneGuard-RI-Environmental-v3"
    assert env_m["feature_count"] == 13
    assert "CHAPALA" in env_m["test_storm"]
    assert "MEGH" in env_m["validation_storm"]
    assert env_m["test_metrics"]["roc_auc"] is not None
    assert len(env_m["limitations"]) >= 3

    # Verify combined multimodal Model STE metadata
    assert "multimodal_model_ste" in data
    ste_m = data["multimodal_model_ste"]
    assert ste_m is not None
    assert ste_m["model_name"] == "CycloneGuard-RI-Multimodal-STE-v3"
    assert ste_m["feature_count"] == 74
    assert "CHAPALA" in ste_m["test_storm"]
    assert "MEGH" in ste_m["validation_storm"]
    assert ste_m["test_metrics"]["roc_auc"] is not None
    assert len(ste_m["limitations"]) >= 3


def test_admin_environmental_model_endpoint(client, admin_auth_headers):
    """GET /admin/models/environmental returns Model E metadata and metrics."""
    response = client.get("/api/v1/admin/models/environmental", headers=admin_auth_headers)
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    data = res["data"]
    assert data["status"] == "Evaluated"
    assert "model_metadata" in data
    assert data["model_metadata"]["feature_count"] == 13


def test_admin_ste_model_endpoint(client, admin_auth_headers):
    """GET /admin/models/ste returns Model STE metadata and metrics."""
    response = client.get("/api/v1/admin/models/ste", headers=admin_auth_headers)
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    data = res["data"]
    assert data["status"] == "Evaluated"
    assert "model_metadata" in data
    assert data["model_metadata"]["feature_count"] == 74


def test_admin_data_sources_includes_environmental(client, admin_auth_headers):
    """GET /admin/data-sources includes NOAA PSL NCEP R2 and OISST v2.0 when include_reanalysis=true."""
    response = client.get("/api/v1/admin/data-sources?include_reanalysis=true", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    source_names = [s["name"] for s in data["data_sources"]]
    assert "NOAA PSL NCEP/DOE Reanalysis 2 (R2)" in source_names
    assert "NOAA PSL OISST v2.0 High-Resolution" in source_names
    assert data["connected_count"] >= 2


def test_environmental_endpoints_require_admin(client, user_auth_headers):
    """Environmental admin endpoints must reject unauthenticated or non-admin requests."""
    # Unauthenticated
    assert client.get("/api/v1/admin/environmental-coverage").status_code == 401
    assert client.get("/api/v1/admin/models/environmental").status_code == 401
    assert client.get("/api/v1/admin/models/ste").status_code == 401

    # Non-admin (standard user)
    assert client.get("/api/v1/admin/environmental-coverage", headers=user_auth_headers).status_code == 403
    assert client.get("/api/v1/admin/models/environmental", headers=user_auth_headers).status_code == 403
    assert client.get("/api/v1/admin/models/ste", headers=user_auth_headers).status_code == 403
