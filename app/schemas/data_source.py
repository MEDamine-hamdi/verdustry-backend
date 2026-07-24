from typing import Optional
from pydantic import BaseModel, ConfigDict


class DataSourceCreate(BaseModel):
    name: str
    sourceType: str  # "excel", "csv", "sql", "api"
    connectionInfo: Optional[str] = None
    companyId: str


class DataSourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    sourceType: str
    connectionInfo: Optional[str] = None
    companyId: str