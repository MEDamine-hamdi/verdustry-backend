from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import require_role
from app.core.tenant import enforce_company_access
from app.services.lca_calculation_service import LcaCalculationService
from app.schemas.lca_calculation import LcaSaveResultRequest, LcaCalculationRequest, LcaCalculationResponse
from app.models.user import User

router = APIRouter(prefix="/lca-calculations", tags=["LCA Calculations"])


@router.get("", response_model=List[LcaCalculationResponse])
def get_lca_calculations(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "ESG_MANAGER", "EXECUTIVE", "AUDITOR")),
):
    enforce_company_access(current_user, company_id)
    service = LcaCalculationService(db)
    return service.get_all(company_id)


@router.post("", response_model=LcaCalculationResponse, status_code=201)
def save_lca_calculation(
    data: LcaSaveResultRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "ESG_MANAGER")),
):
    enforce_company_access(current_user, int(data.companyId))
    service = LcaCalculationService(db)
    request_data = LcaCalculationRequest(
        companyId=data.companyId,
        siteId=data.siteId,
        period=data.period,
        processRef=data.processRef,
        inputData=data.inputData,
        impactMethod=data.impactMethod,
    )
    return service.save_result(
        data=request_data,
        total_carbon_footprint=data.totalCarbonFootprint,
        unit=data.unit,
        result_breakdown=data.resultBreakdown,
    )