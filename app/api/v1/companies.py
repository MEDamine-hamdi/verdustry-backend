from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import require_role
from app.services.company_service import CompanyService
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse
from app.models.user import User

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.get("", response_model=List[CompanyResponse])
def get_companies(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN")),
):
    service = CompanyService(db)
    return service.get_all_companies()


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN")),
):
    service = CompanyService(db)
    return service.get_company(company_id)


@router.post("", response_model=CompanyResponse, status_code=201)
def create_company(
    data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN")),
):
    service = CompanyService(db)
    return service.create_company(data)


@router.put("/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: int,
    data: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN")),
):
    service = CompanyService(db)
    return service.update_company(company_id, data)


@router.delete("/{company_id}")
def delete_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN")),
):
    service = CompanyService(db)
    service.delete_company(company_id)
    return {"ok": True}
