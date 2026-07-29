from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import require_role
from app.core.tenant import enforce_company_access
from app.models.user import User
from app.schemas.anomaly import AnomalyResponse
from app.services.anomaly_service import AnomalyService

router = APIRouter(prefix="/anomalies", tags=["Anomalies"])


@router.get("", response_model=AnomalyResponse)
def get_anomalies(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("ADMIN", "ESG_MANAGER", "EXECUTIVE", "AUDITOR")
    ),
):
    enforce_company_access(current_user, company_id)
    service = AnomalyService(db)
    return service.detect(company_id)