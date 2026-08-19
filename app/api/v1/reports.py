from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import require_role
from app.core.tenant import enforce_company_access
from app.models.user import User
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/{company_id}/pdf")
def get_pdf_report(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "ESG_MANAGER", "EXECUTIVE", "AUDITOR")),
):
    enforce_company_access(current_user, company_id)
    pdf_bytes = ReportService(db).generate_pdf(company_id)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=rapport_esg_{company_id}.pdf"},
    )


@router.get("/{company_id}/excel")
def get_excel_report(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "ESG_MANAGER", "EXECUTIVE", "AUDITOR")),
):
    enforce_company_access(current_user, company_id)
    excel_bytes = ReportService(db).generate_excel(company_id)
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=rapport_esg_{company_id}.xlsx"},
    )