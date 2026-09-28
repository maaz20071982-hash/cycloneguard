"""
Backend API tests for Sprint 11 Final Frozen Production Model endpoints.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.user import User, UserRole


@pytest.fixture
def admin_user():
    return User(
        id="admin-sprint11-test",
        email="admin.sprint11@cycloneguard.org",
        name="Sprint 11 Admin",
        role=UserRole.ADMIN,
        is_active=True,
    )


@pytest.mark.asyncio
async def test_admin_models_includes_final_frozen_model(admin_user):
    """Verify that GET /api/v1/admin/models returns final_frozen_model manifest."""
    from app.api.v1.deps import require_admin
    app.dependency_overrides[require_admin] = lambda: admin_user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/admin/models")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    data = res_data["data"]

    assert data["status"] == "Sprint 11 Multi-Storm Validated & Model Frozen"
    assert "final_frozen_model" in data
    final_model = data["final_frozen_model"]
    assert final_model is not None
    assert final_model["model_version"] == "v3.0.0-frozen"
    assert final_model["feature_count"] == 61
    assert final_model["selected_architecture"] == "Finalist TS (Temporal Kinematics + HURSAT Satellite Spatial Structure)"
    assert final_model["untouched_test_cohort"]["storm"] == "CHAPALA (2015, Arabian Sea)"


@pytest.mark.asyncio
async def test_admin_get_final_frozen_model_endpoint(admin_user):
    """Verify GET /api/v1/admin/models/final endpoint returns complete frozen manifest."""
    from app.api.v1.deps import require_admin
    app.dependency_overrides[require_admin] = lambda: admin_user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/admin/models/final")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    data = res_data["data"]
    assert data["status"] == "Frozen"
    manifest = data["manifest"]
    assert manifest["model_name"] == "CycloneGuard-RI-Multimodal-TS-Final"
    assert manifest["operating_decision_threshold"] == 0.125
    assert len(manifest["feature_list"]) == 61
