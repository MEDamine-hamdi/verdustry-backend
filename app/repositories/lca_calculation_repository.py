from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.lca_calculation import LcaCalculation


class LcaCalculationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, calculation_id: int) -> Optional[LcaCalculation]:
        return self.db.query(LcaCalculation).filter(LcaCalculation.id == calculation_id).first()

    def get_all_by_company(self, company_id: int) -> List[LcaCalculation]:
        return (
            self.db.query(LcaCalculation)
            .filter(LcaCalculation.company_id == company_id)
            .order_by(LcaCalculation.calculated_at.desc())
            .all()
        )

    def create(self, calculation: LcaCalculation) -> LcaCalculation:
        self.db.add(calculation)
        self.db.commit()
        self.db.refresh(calculation)
        return calculation

    def update(self, calculation: LcaCalculation) -> LcaCalculation:
        self.db.commit()
        self.db.refresh(calculation)
        return calculation