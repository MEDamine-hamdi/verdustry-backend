from typing import Optional
from pydantic import BaseModel, ConfigDict


class SiteCreate(BaseModel):
    name: str
    country: Optional[str] = None
    city: Optional[str] = None
    siteType: Optional[str] = None
    address: Optional[str] = None
    companyId: str


class SiteUpdate(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    siteType: Optional[str] = None
    address: Optional[str] = None


class SiteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    country: Optional[str] = None
    city: Optional[str] = None
    siteType: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    companyId: str