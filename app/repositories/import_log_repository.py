from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.import_log import ImportLog


class ImportLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, log_id: int) -> Optional[ImportLog]:
        return self.db.query(ImportLog).filter(ImportLog.id == log_id).first()

    def get_all_by_company(self, company_id: int) -> List[ImportLog]:
        return (
            self.db.query(ImportLog)
            .filter(ImportLog.company_id == company_id)
            .order_by(ImportLog.imported_at.desc())
            .all()
        )

    def create(self, log: ImportLog) -> ImportLog:
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def update(self, log: ImportLog) -> ImportLog:
        self.db.commit()
        self.db.refresh(log)
        return log