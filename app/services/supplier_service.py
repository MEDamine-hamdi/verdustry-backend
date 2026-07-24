from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories.supplier_repository import SupplierRepository
from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate, SupplierUpdate, SupplierResponse


class SupplierService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = SupplierRepository(db)

    def _to_response(self, supplier: Supplier) -> SupplierResponse:
        return SupplierResponse(
            id=str(supplier.id),
            name=supplier.name,
            country=supplier.country,
            sector=supplier.sector,
            companyId=str(supplier.company_id),
        )

    def get_all(self, company_id: int) -> List[SupplierResponse]:
        return [self._to_response(s) for s in self.repo.get_all_by_company(company_id)]

    def create(self, data: SupplierCreate) -> SupplierResponse:
        supplier = Supplier(
            name=data.name,
            country=data.country,
            sector=data.sector,
            company_id=int(data.companyId),
        )
        created = self.repo.create(supplier)
        return self._to_response(created)

    def update(self, supplier_id: int, data: SupplierUpdate) -> SupplierResponse:
        supplier = self.repo.get_by_id(supplier_id)
        if not supplier:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
        if data.name is not None:
            supplier.name = data.name
        if data.country is not None:
            supplier.country = data.country
        if data.sector is not None:
            supplier.sector = data.sector
        updated = self.repo.update(supplier)
        return self._to_response(updated)

    def delete(self, supplier_id: int) -> None:
        supplier = self.repo.get_by_id(supplier_id)
        if not supplier:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
        self.repo.delete(supplier)