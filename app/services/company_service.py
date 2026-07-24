from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories.company_repository import CompanyRepository
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse


class CompanyService:
    def __init__(self, db: Session):
        self.db = db
        self.company_repository = CompanyRepository(db)

    def _to_response(self, company: Company) -> CompanyResponse:
        return CompanyResponse(
            id=str(company.id),
            name=company.name,
            taxId=company.tax_id,
            sector=company.sector,
            country=company.country,
            createdAt=company.created_at,
        )

    def get_company(self, company_id: int) -> CompanyResponse:
        company = self.company_repository.get_by_id(company_id)
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        return self._to_response(company)

    def get_all_companies(self) -> List[CompanyResponse]:
        return [self._to_response(c) for c in self.company_repository.get_all()]

    def create_company(self, data: CompanyCreate) -> CompanyResponse:
        existing = self.company_repository.get_by_tax_id(data.taxId)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tax ID already registered")

        new_company = Company(
            name=data.name,
            tax_id=data.taxId,
            sector=data.sector,
            country=data.country,
        )
        created = self.company_repository.create(new_company)
        return self._to_response(created)

    def update_company(self, company_id: int, data: CompanyUpdate) -> CompanyResponse:
        company = self.company_repository.get_by_id(company_id)
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

        if data.name is not None:
            company.name = data.name
        if data.taxId is not None:
            company.tax_id = data.taxId
        if data.sector is not None:
            company.sector = data.sector
        if data.country is not None:
            company.country = data.country

        updated = self.company_repository.update(company)
        return self._to_response(updated)

    def delete_company(self, company_id: int) -> None:
        company = self.company_repository.get_by_id(company_id)
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        self.company_repository.delete(company)