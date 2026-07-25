from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import require_role
from app.core.tenant import enforce_company_access
from app.services.benchmark_service import BenchmarkService
from app.schemas.benchmark import BenchmarkResponse
from app.models.user import User

router = APIRouter(prefix="/benchmark", tags=["Benchmark"])


@router.get("", response_model=BenchmarkResponse)
def get_benchmark(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "ESG_MANAGER", "EXECUTIVE", "AUDITOR")),
):
    enforce_company_access(current_user, company_id)
    service = BenchmarkService(db)
    return service.get_benchmark(company_id)