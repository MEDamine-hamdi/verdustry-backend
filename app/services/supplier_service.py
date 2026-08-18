from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories.supplier_repository import SupplierRepository
from app.repositories.site_repository import SiteRepository
from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate, SupplierUpdate, SupplierResponse
from app.services.geocoding_service import GeocodingService, GeocodingError
from app.services.distance_service import recompute_supplier_distance


class SupplierService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = SupplierRepository(db)
        self.site_repo = SiteRepository(db)
        self.geocoder = GeocodingService()

    def _to_response(self, supplier: Supplier) -> SupplierResponse:
        return SupplierResponse(
            id=str(supplier.id),
            name=supplier.name,
            country=supplier.country,
            sector=supplier.sector,
            address=supplier.address,
            latitude=supplier.latitude,
            longitude=supplier.longitude,
            siteId=str(supplier.site_id) if supplier.site_id else None,
            distanceKm=supplier.distance_km,
            companyId=str(supplier.company_id),
        )

    def get_all(self, company_id: int) -> List[SupplierResponse]:
        return [self._to_response(s) for s in self.repo.get_all_by_company(company_id)]

    def _geocode_if_needed(self, supplier: Supplier):
        if not supplier.address:
            return
        try:
            lat, lon = self.geocoder.geocode(supplier.address)
            supplier.latitude = lat
            supplier.longitude = lon
        except GeocodingError:
            pass

    def _update_distance(self, supplier: Supplier):
        if not supplier.site_id:
            return
        site = self.site_repo.get_by_id(supplier.site_id)
        if site:
            recompute_supplier_distance(supplier, site)

    def create(self, data: SupplierCreate) -> SupplierResponse:
        supplier = Supplier(
            name=data.name,
            country=data.country,
            sector=data.sector,
            address=data.address,
            site_id=int(data.siteId) if data.siteId else None,
            company_id=int(data.companyId),
        )
        self._geocode_if_needed(supplier)
        self._update_distance(supplier)
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

        address_changed = data.address is not None and data.address != supplier.address
        if data.address is not None:
            supplier.address = data.address
        if address_changed:
            self._geocode_if_needed(supplier)

        site_changed = data.siteId is not None and data.siteId != (
            str(supplier.site_id) if supplier.site_id else None
        )
        if data.siteId is not None:
            supplier.site_id = int(data.siteId) if data.siteId else None

        if address_changed or site_changed:
            self._update_distance(supplier)

        updated = self.repo.update(supplier)
        return self._to_response(updated)

    def delete(self, supplier_id: int) -> None:
        supplier = self.repo.get_by_id(supplier_id)
        if not supplier:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
        self.repo.delete(supplier)