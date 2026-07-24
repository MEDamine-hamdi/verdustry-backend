from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import require_role
from app.services.site_service import SiteService
from app.schemas.site import SiteCreate, SiteUpdate, SiteResponse
from app.models.user import User

router = APIRouter(prefix="/sites", tags=["Sites"])


@router.get("", response_model=List[SiteResponse])
def get_sites(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "ESG_MANAGER", "EXECUTIVE", "AUDITOR")),
):
    service = SiteService(db)
    return service.get_all(company_id)


@router.post("", response_model=SiteResponse, status_code=201)
def create_site(
    data: SiteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "ESG_MANAGER")),
):
    service = SiteService(db)
    return service.create(data)


@router.put("/{site_id}", response_model=SiteResponse)
def update_site(
    site_id: int,
    data: SiteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "ESG_MANAGER")),
):
    service = SiteService(db)
    return service.update(site_id, data)


@router.delete("/{site_id}")
def delete_site(
    site_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "ESG_MANAGER")),
):
    service = SiteService(db)
    service.delete(site_id)
    return {"ok": True}