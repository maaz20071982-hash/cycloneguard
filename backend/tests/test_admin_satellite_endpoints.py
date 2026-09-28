"""
Tests for Admin Satellite Coverage and Data Source Endpoints.
Sprint 7 - Phase 15 Verification.
"""

import pytest


def test_satellite_coverage_unauthenticated(client):
    """Unauthenticated request must be rejected with 401."""
    res = client.get("/api/v1/admin/satellite-coverage")
    assert res.status_code == 401


def test_satellite_coverage_forbidden_for_user(client, user_auth_headers):
    """Standard user must be rejected with 403."""
    res = client.get("/api/v1/admin/satellite-coverage", headers=user_auth_headers)
    assert res.status_code == 403


def test_satellite_coverage_admin_success(client, admin_auth_headers):
    """Admin must receive real satellite coverage metrics with truthful counts."""
    res = client.get("/api/v1/admin/satellite-coverage", headers=admin_auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    data = body["data"]

    # Verify real fields without fabrication
    assert data["source_count"] >= 6
    assert data["observation_count"] == 400
    assert data["matched_observations"] == 1
    assert data["ir_matched_observations"] == 1
    assert data["microwave_matched_observations"] == 0
    assert data["scatterometer_matched_observations"] == 0
    assert data["rejected_observations"] == 0
    assert data["coverage_percentage"] == 0.25
    assert "VALID" in data["data_quality_status"]

    # Verify sources list
    by_src = {s["source_id"]: s for s in data["coverage_by_source"]}
    assert "noaa_hursat_b1" in by_src
    assert by_src["noaa_hursat_b1"]["status"] == "ALIGNED"
    assert by_src["noaa_hursat_b1"]["matched_observations"] == "1"

    assert "isro_insat3d_mosdac" in by_src
    assert by_src["isro_insat3d_mosdac"]["status"] == "DOCUMENTED"
    assert by_src["isro_insat3d_mosdac"]["available_data"] == "Not available"


def test_admin_data_sources_status(client, admin_auth_headers):
    """Admin data sources endpoint reports operational feeds."""
    res = client.get("/api/v1/admin/data-sources", headers=admin_auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    data = body["data"]
    assert data["total"] == 6


def test_historical_hursat_coverage_admin_success(client, admin_auth_headers):
    """Admin endpoint for historical HURSAT coverage must report real Sprint 8 counts."""
    res = client.get("/api/v1/admin/historical-hursat-coverage", headers=admin_auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    data = body["data"]

    # Verify Sprint 8 exact computed metrics
    assert data["dataset_version"] == "cycloneguard-satellite-hursat-v2"
    assert data["historical_assets"] == 287
    assert data["downloaded_assets"] >= 887
    assert data["valid_assets"] >= 887
    assert data["corrupted_assets"] == 0
    assert data["cyclone_matches"] == 347
    assert data["patches"] == 1020
    assert data["ri_labeled_samples"] == 299
    assert data["ri_positive_samples"] == 39
    assert data["ri_negative_samples"] == 260
    assert data["unique_storms"] == 6
    assert "B" in data["dataset_readiness_classification"]

