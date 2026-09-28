from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from app.repositories.audit_repo import AuditRepository


class AuditService:
    def __init__(self, db: Session):
        self.db = db
        self.audit_repo = AuditRepository(db)

    def record_event(
        self,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """Record an administrative or security event without passwords or secrets."""
        # Sanitize metadata to guarantee no secrets, passwords, or tokens leak into audit trail
        sanitized_meta = None
        if metadata:
            sanitized_meta = {}
            for k, v in metadata.items():
                if any(secret_term in k.lower() for secret_term in ["pass", "token", "secret", "auth", "key"]):
                    continue
                sanitized_meta[k] = v

        return self.audit_repo.log(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            metadata=sanitized_meta,
        )

    def list_events(
        self,
        skip: int = 0,
        limit: int = 50,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
    ) -> Tuple[List[AuditLog], int]:
        return self.audit_repo.list_logs(
            skip=skip,
            limit=limit,
            action=action,
            resource_type=resource_type,
        )
