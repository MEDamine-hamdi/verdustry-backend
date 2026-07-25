from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import require_role
from app.core.tenant import enforce_company_access
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import EmissionAggregateResponse, TrendResponse, TopEmittersResponse
from app.models.user import User

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/aggregate", response_model=EmissionAggregateResponse)
def get_aggregate(
    company_id: int,
    group_by: str = "scope",
    scope: Optional[int] = None,
    site_id: Optional[int] = None,
    period_from: Optional[str] = None,
    period_to: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "ESG_MANAGER", "EXECUTIVE", "AUDITOR")),
):
    enforce_company_access(current_user, company_id)
    service = AnalyticsService(db)
    return service.aggregate(company_id, group_by, scope, site_id, period_from, period_to)


@router.get("/trend", response_model=TrendResponse)
def get_trend(
    company_id: int,
    scope: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "ESG_MANAGER", "EXECUTIVE", "AUDITOR")),
):
    enforce_company_access(current_user, company_id)
    service = AnalyticsService(db)
    return service.trend(company_id, scope)


@router.get("/top-emitters", response_model=TopEmittersResponse)
def get_top_emitters(
    company_id: int,
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "ESG_MANAGER", "EXECUTIVE", "AUDITOR")),
):
    enforce_company_access(current_user, company_id)
    service = AnalyticsService(db)
    return service.top_emitters(company_id, limit)