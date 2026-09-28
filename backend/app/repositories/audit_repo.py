from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.orm import Session, joinedload
from app.models.audit_log import AuditLog
from app.repositories.base_repo import BaseRepository


class AuditRepository(BaseRepository[AuditLog]):
    def __init__(self, db: Session):
        super().__init__(AuditLog, db)

    def log(
        self,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """Create and persist an immutable audit log entry."""
        audit_entry = AuditLog(
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            user_id=user_id,
            metadata_json=metadata,
        )
        return self.create(audit_entry)

    def list_logs(
        self,
        skip: int = 0,
        limit: int = 50,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
    ) -> Tuple[List[AuditLog], int]:
        """Fetch audit log records ordered chronologically descending."""
        query = self.db.query(AuditLog).options(joinedload(AuditLog.user))
        if action:
            query = query.filter(AuditLog.action == action)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)

        total = query.count()
        logs = query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
        return logs, total
