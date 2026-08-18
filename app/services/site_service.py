from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories.site_repository import SiteRepository
from app.repositories.supplier_repository import SupplierRepository
from app.models.site import Site
from app.schemas.site import SiteCreate, SiteUpdate, SiteResponse
from app.services.geocoding_service import GeocodingService, GeocodingError
from app.services.distance_service import recompute_supplier_distance


class SiteService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = SiteRepository(db)
        self.supplier_repo = SupplierRepository(db)
        self.geocoder = GeocodingService()

    def _to_response(self, site: Site) -> SiteResponse:
        return SiteResponse(
            id=str(site.id),
            name=site.name,
            country=site.country,
            city=site.city,
            siteType=site.site_type,
            address=site.address,
            latitude=site.latitude,
            longitude=site.longitude,
            companyId=str(site.company_id),
        )

    def get_all(self, company_id: int) -> List[SiteResponse]:
        return [self._to_response(s) for s in self.repo.get_all_by_company(company_id)]

    def _geocode_if_needed(self, site: Site):
        if not site.address:
            return
        try:
            lat, lon = self.geocoder.geocode(site.address)
            site.latitude = lat
            site.longitude = lon
        except GeocodingError:
            # On n'échoue pas la création/modification du site si le géocodage échoue —
            # l'adresse reste enregistrée, les coordonnées resteront vides.
            pass

    def create(self, data: SiteCreate) -> SiteResponse:
        site = Site(
            name=data.name,
            country=data.country,
            city=data.city,
            site_type=data.siteType,
            address=data.address,
            company_id=int(data.companyId),
        )
        self._geocode_if_needed(site)
        created = self.repo.create(site)
        return self._to_response(created)

    def update(self, site_id: int, data: SiteUpdate) -> SiteResponse:
        site = self.repo.get_by_id(site_id)
        if not site:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")
        if data.name is not None:
            site.name = data.name
        if data.country is not None:
            site.country = data.country
        if data.city is not None:
            site.city = data.city
        if data.siteType is not None:
            site.site_type = data.siteType

        address_changed = data.address is not None and data.address != site.address
        if data.address is not None:
            site.address = data.address
        if address_changed:
            self._geocode_if_needed(site)

        updated = self.repo.update(site)

        # Si l'adresse du site a changé, on recalcule la distance de tous les fournisseurs liés.
        if address_changed:
            linked_suppliers = [
                s for s in self.supplier_repo.get_all_by_company(updated.company_id) if s.site_id == updated.id
            ]
            for supplier in linked_suppliers:
                recompute_supplier_distance(supplier, updated)
                self.supplier_repo.update(supplier)

        return self._to_response(updated)

    def delete(self, site_id: int) -> None:
        site = self.repo.get_by_id(site_id)
        if not site:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")
        self.repo.delete(site)