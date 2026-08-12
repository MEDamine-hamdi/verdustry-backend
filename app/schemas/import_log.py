from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ImportLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    dataSourceId: str
    companyId: str
    importedById: Optional[str] = None
    status: str
    rowsTotal: Optional[int] = None
    rowsImported: Optional[int] = None
    rowsFailed: Optional[int] = None
    errorMessage: Optional[str] = None
    importedAt: Optional[datetime] = None


class SqlImportRequest(BaseModel):
    connectionUrl: str
    query: str
    companyId: str


class ApiImportRequest(BaseModel):
    url: str
    authHeader: Optional[str] = None
    companyId: str

class OdooImportRequest(BaseModel):
    companyId: str