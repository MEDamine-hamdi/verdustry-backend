from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories.site_repository import SiteRepository
from app.models.site import Site
from app.schemas.site import SiteCreate, SiteUpdate, SiteResponse


class SiteService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = SiteRepository(db)

    def _to_response(self, site: Site) -> SiteResponse:
        return SiteResponse(
            id=str(site.id),
            name=site.name,
            country=site.country,
            city=site.city,
            siteType=site.site_type,
            companyId=str(site.company_id),
        )

    def get_all(self, company_id: int) -> List[SiteResponse]:
        return [self._to_response(s) for s in self.repo.get_all_by_company(company_id)]

    def create(self, data: SiteCreate) -> SiteResponse:
        site = Site(
            name=data.name,
            country=data.country,
            city=data.city,
            site_type=data.siteType,
            company_id=int(data.companyId),
        )
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
        updated = self.repo.update(site)
        return self._to_response(updated)

    def delete(self, site_id: int) -> None:
        site = self.repo.get_by_id(site_id)
        if not site:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")
        self.repo.delete(site)