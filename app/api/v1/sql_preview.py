from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import require_role
from app.services.sql_preview_service import SqlPreviewService, SqlPreviewError
from app.schemas.sql_preview import SqlPreviewRequest, SqlPreviewResponse
from app.models.user import User

router = APIRouter(prefix="/sql-preview", tags=["SQL Preview"])


@router.post("", response_model=SqlPreviewResponse)
def preview_sql(
    data: SqlPreviewRequest,
    current_user: User = Depends(require_role("ADMIN", "ESG_MANAGER")),
):
    service = SqlPreviewService()
    try:
        rows = service.run_query(data.connectionUrl, data.query)
    except SqlPreviewError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return SqlPreviewResponse(rows=rows)