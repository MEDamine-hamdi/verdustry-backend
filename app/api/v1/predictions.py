from fastapi import APIRouter, Depends

from app.core.security import require_role
from app.services.ml_prediction_service import ml_service
from app.schemas.prediction import (
    OvershootPredictionRequest,
    OvershootPredictionResponse,
    CostPredictionRequest,
    CostPredictionResponse,
)
from app.models.user import User

router = APIRouter(prefix="/predictions", tags=["Predictions (ML - experimental)"])


@router.post("/overshoot-risk", response_model=OvershootPredictionResponse)
def predict_overshoot_risk(
    data: OvershootPredictionRequest,
    current_user: User = Depends(require_role("ADMIN", "ESG_MANAGER", "EXECUTIVE")),
):
    result = ml_service.predict_overshoot_risk(
        sector=data.sector,
        emissions_tco2e=data.emissionsTco2e,
        production_volume=data.productionVolume,
        emissions_ma3=data.emissionsMa3,
        emissions_trend_3m=data.emissionsTrend3m,
        target_trend_3m=data.targetTrend3m,
        gap_to_target_pct=data.gapToTargetPct,
        cbam_exposure_ratio=data.cbamExposureRatio,
        eu_export_share=data.euExportShare,
    )
    return OvershootPredictionResponse(**result)


@router.post("/cbam-cost", response_model=CostPredictionResponse)
def predict_cbam_cost(
    data: CostPredictionRequest,
    current_user: User = Depends(require_role("ADMIN", "ESG_MANAGER", "EXECUTIVE")),
):
    result = ml_service.predict_cbam_cost(
        sector=data.sector,
        emissions_tco2e=data.emissionsTco2e,
        production_volume=data.productionVolume,
        cbam_exposure_ratio=data.cbamExposureRatio,
        eu_export_share=data.euExportShare,
        cbam_price_eur_tco2e=data.cbamPriceEurTco2e,
        free_allocation_pct=data.freeAllocationPct,
    )
    return CostPredictionResponse(**result)