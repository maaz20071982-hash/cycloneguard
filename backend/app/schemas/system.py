from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str = "ok"
    timestamp: str
    application: str = "ok"
    database: str
    ai_engine: str = "not_deployed"
    data_pipeline: str = "not_connected"
    version: str
    environment: str = "production"


class SystemInfoResponse(BaseModel):
    app_name: str
    version: str
    environment: str
    platform_status: str
    research_status: str
    database_connected: bool
    application_status: str = "operational"
    ai_engine_status: str = "not_deployed"
    data_pipeline_status: str = "not_connected"
    data_sources_status: str
    model_inference_status: str
    active_sprint: str
