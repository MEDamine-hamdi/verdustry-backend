from typing import Optional, List
from pydantic import BaseModel


class EmissionAggregateItem(BaseModel):
    key: str  # ex: nom du site, scope, période, etc. selon le groupBy
    totalValue: float
    unit: str = "tCO2e"


class EmissionAggregateResponse(BaseModel):
    groupBy: str
    items: List[EmissionAggregateItem]
    totalValue: float


class TrendPoint(BaseModel):
    period: str
    value: float


class TrendResponse(BaseModel):
    points: List[TrendPoint]
    changePercent: Optional[float] = None  # évolution dernière période vs précédente


class TopEmitterItem(BaseModel):
    category: str
    totalValue: float
    percentOfTotal: float


class TopEmittersResponse(BaseModel):
    items: List[TopEmitterItem]