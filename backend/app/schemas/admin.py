from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.user import UserRole
from app.schemas.user import UserResponse


class UserUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="Full name of user")
    role: Optional[UserRole] = Field(None, description="System role assignment")


class UserStatusUpdateRequest(BaseModel):
    is_active: bool = Field(..., description="Active or suspended status")


class AuditLogResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class AuditLogsListResponse(BaseModel):
    logs: List[AuditLogResponse]
    total: int
    skip: int
    limit: int


class DataSourceDetail(BaseModel):
    name: str
    provider: str
    type: str
    status: str
    last_successful_update: Optional[str] = None
    last_failure: Optional[str] = None
    data_coverage: str
    records_processed: Optional[int] = None
    channels: List[str] = []
    actions: List[str] = ["View", "Configure", "Test Connection"]


class ModelDetail(BaseModel):
    model_name: str
    version: str
    status: str
    framework: str
    dataset: str
    dataset_version: Optional[str] = None
    evaluation: Optional[Dict[str, Any]] = None
    deployment_status: str
    deployed: bool = False
    target: str
    trained_at: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None


class AdminDashboardResponse(BaseModel):
    data_sources: Dict[str, Any]
    models: Dict[str, Any]
    predictions: Dict[str, Any]
    alerts: Dict[str, Any]
    users: Dict[str, Any]
    health: Dict[str, Any]
    recent_activity: List[AuditLogResponse]
