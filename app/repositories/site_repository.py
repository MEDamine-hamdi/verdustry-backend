from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.site import Site


class SiteRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, site_id: int) -> Optional[Site]:
        return self.db.query(Site).filter(Site.id == site_id).first()

    def get_all_by_company(self, company_id: int) -> List[Site]:
        return self.db.query(Site).filter(Site.company_id == company_id).all()

    def create(self, site: Site) -> Site:
        self.db.add(site)
        self.db.commit()
        self.db.refresh(site)
        return site

    def update(self, site: Site) -> Site:
        self.db.commit()
        self.db.refresh(site)
        return site

    def delete(self, site: Site) -> None:
        self.db.delete(site)
        self.db.commit()