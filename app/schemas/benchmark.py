from typing import Optional, List
from pydantic import BaseModel


class BenchmarkGapItem(BaseModel):
    referenceType: str  # "sector_average", "net_zero", "sbti", "csrd", "cbam"
    label: Optional[str] = None
    referenceValue: float
    companyValue: float
    gapValue: float  # companyValue - referenceValue
    gapPercent: float  # (gapValue / referenceValue) * 100
    year: Optional[int] = None
    unit: str = "tCO2e"


class BenchmarkResponse(BaseModel):
    sector: str
    companyTotalEmissions: float
    items: List[BenchmarkGapItem]