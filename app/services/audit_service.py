from typing import Optional
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditService:
    def __init__(self, db: Session):
        self.db = db

    def log(
        self,
        actor_id: Optional[int],
        action: str,
        target_type: str,
        target_id: Optional[str] = None,
        details: Optional[str] = None,
    ) -> None:
        entry = AuditLog(
            actor_id=actor_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details,
        )
        self.db.add(entry)
        self.db.commit()