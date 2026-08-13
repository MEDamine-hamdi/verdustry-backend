from typing import Optional
from pydantic import BaseModel, ConfigDict


class SupplierCreate(BaseModel):
    name: str
    country: Optional[str] = None
    sector: Optional[str] = None
    siteId: Optional[str] = None
    distanceKm: Optional[float] = None
    companyId: str


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None
    sector: Optional[str] = None
    siteId: Optional[str] = None
    distanceKm: Optional[float] = None


class SupplierResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    country: Optional[str] = None
    sector: Optional[str] = None
    siteId: Optional[str] = None
    distanceKm: Optional[float] = None
    companyId: str