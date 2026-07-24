from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class CompanyCreate(BaseModel):
    name: str
    taxId: str
    sector: Optional[str] = None
    country: Optional[str] = None


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    taxId: Optional[str] = None
    sector: Optional[str] = None
    country: Optional[str] = None


class CompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    taxId: str
    sector: Optional[str] = None
    country: Optional[str] = None
    createdAt: Optional[datetime] = None