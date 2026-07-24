from typing import Optional
from datetime import date
from pydantic import BaseModel, ConfigDict


class TargetCreate(BaseModel):
    name: str
    metric: str
    baselineValue: Optional[float] = None
    baselineYear: Optional[int] = None
    targetValue: Optional[float] = None
    targetYear: Optional[int] = None
    deadline: Optional[date] = None
    companyId: str


class TargetUpdate(BaseModel):
    name: Optional[str] = None
    metric: Optional[str] = None
    baselineValue: Optional[float] = None
    baselineYear: Optional[int] = None
    targetValue: Optional[float] = None
    targetYear: Optional[int] = None
    deadline: Optional[date] = None


class TargetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    metric: str
    baselineValue: Optional[float] = None
    baselineYear: Optional[int] = None
    targetValue: Optional[float] = None
    targetYear: Optional[int] = None
    deadline: Optional[date] = None
    companyId: str