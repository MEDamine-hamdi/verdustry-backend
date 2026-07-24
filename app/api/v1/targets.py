from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import require_role
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
    service = TargetService(db)
    return service.get_all(company_id)


@router.post("", response_model=TargetResponse, status_code=201)
def create_target(
    data: TargetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "ESG_MANAGER")),
):
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
    return service.update(target_id, data)


@router.delete("/{target_id}")
def delete_target(
    target_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "ESG_MANAGER")),
):
    service = TargetService(db)
    service.delete(target_id)
    return {"ok": True}