from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel


class AnomalyAlert(BaseModel):
    type: Literal["unusual_spike", "indicator_inconsistency"]
    severity: Literal["high", "medium", "low"]
    period: str
    message: str
    value: float
    score: float
    details: Optional[Dict[str, Any]] = None


class AnomalySummary(BaseModel):
    high: int = 0
    medium: int = 0
    low: int = 0
    total: int = 0


class AnomalyResponse(BaseModel):
    alerts: List[AnomalyAlert]
    summary: AnomalySummary