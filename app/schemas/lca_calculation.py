from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class LcaCalculationRequest(BaseModel):
    companyId: str
    siteId: Optional[str] = None
    importLogId: Optional[str] = None
    period: Optional[str] = None
    processRef: str  # nom ou UUID du process/product system openLCA à utiliser
    inputData: Dict[str, Any]  # flux/quantités envoyés à openLCA, ex: {"steel_kg": 500, "electricity_kwh": 1200}
    impactMethod: Optional[str] = "IPCC 2021 GWP100"


class LcaCalculationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    companyId: str
    siteId: Optional[str] = None
    importLogId: Optional[str] = None
    period: Optional[str] = None
    processRef: Optional[str] = None
    inputData: Optional[Dict[str, Any]] = None
    impactMethod: Optional[str] = None
    totalCarbonFootprint: Optional[float] = None
    unit: Optional[str] = None
    resultBreakdown: Optional[Dict[str, Any]] = None
    status: str
    errorMessage: Optional[str] = None
    calculatedAt: Optional[datetime] = None