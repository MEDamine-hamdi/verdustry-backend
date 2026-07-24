from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.company import Company


class CompanyRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, company_id: int) -> Optional[Company]:
        return self.db.query(Company).filter(Company.id == company_id).first()

    def get_by_tax_id(self, tax_id: str) -> Optional[Company]:
        return self.db.query(Company).filter(Company.tax_id == tax_id).first()

    def get_all(self) -> List[Company]:
        return self.db.query(Company).all()

    def create(self, company: Company) -> Company:
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        return company

    def update(self, company: Company) -> Company:
        self.db.commit()
        self.db.refresh(company)
        return company

    def delete(self, company: Company) -> None:
        self.db.delete(company)
        self.db.commit()