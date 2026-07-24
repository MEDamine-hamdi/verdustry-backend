from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.target import Target


class TargetRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, target_id: int) -> Optional[Target]:
        return self.db.query(Target).filter(Target.id == target_id).first()

    def get_all_by_company(self, company_id: int) -> List[Target]:
        return self.db.query(Target).filter(Target.company_id == company_id).all()

    def create(self, target: Target) -> Target:
        self.db.add(target)
        self.db.commit()
        self.db.refresh(target)
        return target

    def update(self, target: Target) -> Target:
        self.db.commit()
        self.db.refresh(target)
        return target

    def delete(self, target: Target) -> None:
        self.db.delete(target)
        self.db.commit()