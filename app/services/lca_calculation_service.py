from typing import List
from sqlalchemy.orm import Session

from app.models.lca_calculation import LcaCalculation
from app.repositories.lca_calculation_repository import LcaCalculationRepository
from app.schemas.lca_calculation import LcaCalculationRequest, LcaCalculationResponse


class LcaCalculationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = LcaCalculationRepository(db)

    def _to_response(self, calc: LcaCalculation) -> LcaCalculationResponse:
        return LcaCalculationResponse(
            id=str(calc.id),
            companyId=str(calc.company_id),
            siteId=str(calc.site_id) if calc.site_id else None,
            importLogId=str(calc.import_log_id) if calc.import_log_id else None,
            period=calc.period,
            scope=calc.scope,
            processRef=calc.process_ref,
            inputData=calc.input_data,
            impactMethod=calc.impact_method,
            totalCarbonFootprint=calc.total_carbon_footprint,
            unit=calc.unit,
            resultBreakdown=calc.result_breakdown,
            status=calc.status,
            errorMessage=calc.error_message,
            calculatedAt=calc.calculated_at,
        )

    def get_all(self, company_id: int) -> List[LcaCalculationResponse]:
        return [self._to_response(c) for c in self.repo.get_all_by_company(company_id)]

    def save_result(
        self,
        data: LcaCalculationRequest,
        total_carbon_footprint: float,
        unit: str,
        result_breakdown: dict,
    ) -> LcaCalculationResponse:
        calc = LcaCalculation(
            company_id=int(data.companyId),
            site_id=int(data.siteId) if data.siteId else None,
            import_log_id=int(data.importLogId) if data.importLogId else None,
            period=data.period,
            scope=data.scope,
            process_ref=data.processRef,
            input_data=data.inputData,
            impact_method=data.impactMethod,
            total_carbon_footprint=total_carbon_footprint,
            unit=unit,
            result_breakdown=result_breakdown,
            status="success",
        )
        created = self.repo.create(calc)
        return self._to_response(created)