from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import require_role
from app.core.tenant import enforce_company_access
from app.services.target_service import TargetService
from app.schemas.target import TargetCreate, TargetUpdate, TargetResponse
from app.models.user import User

router = APIRouter(prefix="/targets", tags=["Targets"])


@router.get("", response_model=List[TargetResponse])
def get_targets(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "ESG_MANAGER", "EXECUTIVE", "AUDITOR")),
):
    enforce_company_access(current_user, company_id)
    service = TargetService(db)
    return service.get_all(company_id)


@router.post("", response_model=TargetResponse, status_code=201)
def create_target(
    data: TargetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "ESG_MANAGER")),
):
    enforce_company_access(current_user, int(data.companyId))
    service = TargetService(db)
    return service.create(data)


@router.put("/{target_id}", response_model=TargetResponse)
def update_target(
    target_id: int,
    data: TargetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "ESG_MANAGER")),
):
    service = TargetService(db)
    target = service.repo.get_by_id(target_id)
    if target:
        enforce_company_access(current_user, target.company_id)
    return service.update(target_id, data)


@router.delete("/{target_id}")
def delete_target(
    target_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "ESG_MANAGER")),
):
    service = TargetService(db)
    target = service.repo.get_by_id(target_id)
    if target:
        enforce_company_access(current_user, target.company_id)
    service.delete(target_id)
    return {"ok": True}