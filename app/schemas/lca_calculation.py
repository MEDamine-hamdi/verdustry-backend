from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class LcaCalculationRequest(BaseModel):
    companyId: str
    siteId: Optional[str] = None
    importLogId: Optional[str] = None
    period: Optional[str] = None
    processRef: str
    inputData: Dict[str, Any]
    impactMethod: Optional[str] = "IPCC 2021 GWP100"


class LcaSaveResultRequest(BaseModel):
    """Payload envoyé par le front après un calcul déjà effectué (mock ou réel)."""
    companyId: str
    siteId: Optional[str] = None
    period: Optional[str] = None
    processRef: str
    inputData: Dict[str, Any]
    impactMethod: Optional[str] = "Test GWP Method"
    totalCarbonFootprint: float
    unit: str = "kgCO2e"
    resultBreakdown: List[Dict[str, Any]]


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
    resultBreakdown: Optional[Any] = None
    status: str
    errorMessage: Optional[str] = None
    calculatedAt: Optional[datetime] = None