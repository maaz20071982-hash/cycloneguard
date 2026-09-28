from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class CyclonePlaceholderResponse(BaseModel):
    message: str = "No operational cyclone data is currently connected."
    demonstration_data: bool = False
    connected_data_sources: List[str] = []
    status: str = "Awaiting data source ingestion pipeline"


class AIModelStatusResponse(BaseModel):
    model_name: str
    version: str
    status: str
    deployed: bool = False
    architecture: Optional[str] = None
    note: str = "Model weights will be trained and deployed in subsequent sprints."


class PredictionPlaceholderResponse(BaseModel):
    message: str = "AI prediction engine is not deployed in Sprint 1."
    status: str = "Coming in the next development phase"
    active_predictions_count: int = 0
