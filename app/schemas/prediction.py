from pydantic import BaseModel


class OvershootPredictionRequest(BaseModel):
    sector: str
    emissionsTco2e: float
    productionVolume: float
    emissionsMa3: float
    emissionsTrend3m: float
    targetTrend3m: float
    gapToTargetPct: float
    cbamExposureRatio: float
    euExportShare: float


class OvershootPredictionResponse(BaseModel):
    overshootRisk: bool
    probability: float


class CostPredictionRequest(BaseModel):
    sector: str
    emissionsTco2e: float
    productionVolume: float
    cbamExposureRatio: float
    euExportShare: float
    cbamPriceEurTco2e: float
    freeAllocationPct: float


class CostPredictionResponse(BaseModel):
    predictedCostTnd: float