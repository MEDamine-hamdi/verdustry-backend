from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import require_role
from app.services.import_service import ImportService
from app.services.sql_import_service import SqlImportService
from app.services.api_import_service import ApiImportService
from app.repositories.data_source_repository import DataSourceRepository
from app.models.data_source import DataSource
from app.models.user import User
from app.schemas.import_log import ImportLogResponse, SqlImportRequest, ApiImportRequest

router = APIRouter(prefix="/imports", tags=["Imports"])


def _to_response(log) -> ImportLogResponse:
    return ImportLogResponse(
        id=str(log.id),
        dataSourceId=str(log.data_source_id),
        companyId=str(log.company_id),
        importedById=str(log.imported_by_id) if log.imported_by_id else None,
        status=log.status,
        rowsTotal=log.rows_total,
        rowsImported=log.rows_imported,
        rowsFailed=log.rows_failed,
        errorMessage=log.error_message,
        importedAt=log.imported_at,
    )


@router.post("/emissions/excel", response_model=ImportLogResponse)
def import_emissions_excel(
    company_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "ESG_MANAGER")),
):
    ds_repo = DataSourceRepository(db)
    data_source = DataSource(
        name=file.filename,
        source_type="excel" if file.filename.endswith((".xlsx", ".xls")) else "csv",
        company_id=company_id,
    )
    data_source = ds_repo.create(data_source)

    service = ImportService(db)
    log = service.import_emissions(
        file=file.file,
        filename=file.filename,
        company_id=company_id,
        user_id=current_user.id,
        data_source_id=data_source.id,
    )
    return _to_response(log)


@router.post("/emissions/sql", response_model=ImportLogResponse)
def import_emissions_sql(
    data: SqlImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "ESG_MANAGER")),
):
    ds_repo = DataSourceRepository(db)
    data_source = DataSource(
        name="Import SQL",
        source_type="sql",
        connection_info=data.connectionUrl,
        company_id=int(data.companyId),
    )
    data_source = ds_repo.create(data_source)

    service = SqlImportService(db)
    log = service.import_emissions_from_sql(
        connection_url=data.connectionUrl,
        query=data.query,
        company_id=int(data.companyId),
        user_id=current_user.id,
        data_source_id=data_source.id,
    )
    return _to_response(log)


@router.post("/emissions/api", response_model=ImportLogResponse)
def import_emissions_api(
    data: ApiImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "ESG_MANAGER")),
):
    ds_repo = DataSourceRepository(db)
    data_source = DataSource(
        name="Import API REST",
        source_type="api",
        connection_info=data.url,
        company_id=int(data.companyId),
    )
    data_source = ds_repo.create(data_source)

    service = ApiImportService(db)
    log = service.import_emissions_from_api(
        url=data.url,
        auth_header=data.authHeader,
        company_id=int(data.companyId),
        user_id=current_user.id,
        data_source_id=data_source.id,
    )
    return _to_response(log)