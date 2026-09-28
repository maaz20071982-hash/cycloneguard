import os
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.config import settings
from app.core.database import get_db
from app.core.responses import success_response
from app.schemas.system import HealthResponse, SystemInfoResponse

router = APIRouter(tags=["System"])


@router.get("/health", summary="Health check endpoint")
def health_check(db: Session = Depends(get_db)):
    """Health check probing separate application, database, AI engine, and data pipeline components."""
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "application": "ok",
        "database": db_status,
        "ai_engine": "not_deployed",
        "data_pipeline": "not_connected",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@router.get("/system/info", summary="Application runtime status and capability information")
def system_info(db: Session = Depends(get_db)):
    """Return truthful application environment metadata without exposing secrets."""
    db_connected = False
    try:
        db.execute(text("SELECT 1"))
        db_connected = True
    except Exception:
        db_connected = False

    ri_meta_path = os.path.join(settings.PROJECT_ROOT, "models", "ri", "v1", "metadata.json")
    has_ri_model = os.path.exists(ri_meta_path)

    info = SystemInfoResponse(
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        platform_status="operational",
        research_status="Research & Demonstration Platform",
        database_connected=db_connected,
        application_status="operational",
        ai_engine_status="operational_v1" if has_ri_model else "not_deployed",
        data_pipeline_status="not_connected",
        data_sources_status="Observational track & sample satellite crops staged",
        model_inference_status="Sprint 6 RI Model v1 deployed (24h horizon, Delta V >= 30 kts)" if has_ri_model else "Not deployed (Sprint 3 admin foundation)",
        active_sprint="Sprint 6 - Rapid Intensification Model v1",
    )
    return success_response(data=info.model_dump())
