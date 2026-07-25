from typing import List
from sqlalchemy.orm import Session

from app.models.emission import Emission
from app.models.company import Company
from app.models.benchmark_reference import BenchmarkReference
from app.schemas.benchmark import BenchmarkGapItem, BenchmarkResponse


class BenchmarkService:
    def __init__(self, db: Session):
        self.db = db

    def get_benchmark(self, company_id: int) -> BenchmarkResponse:
        company = self.db.query(Company).filter(Company.id == company_id).first()
        sector = company.sector if company and company.sector else "Manufacturing"

        total_emissions = (
            self.db.query(Emission)
            .filter(Emission.company_id == company_id)
            .all()
        )
        company_total = sum(e.value for e in total_emissions)

        references = (
            self.db.query(BenchmarkReference)
            .filter(BenchmarkReference.sector == sector)
            .all()
        )

        items: List[BenchmarkGapItem] = []
        for ref in references:
            gap_value = round(company_total - ref.value, 2)
            gap_percent = round((gap_value / ref.value * 100) if ref.value != 0 else 0, 1)
            items.append(
                BenchmarkGapItem(
                    referenceType=ref.reference_type,
                    label=ref.label,
                    referenceValue=ref.value,
                    companyValue=round(company_total, 2),
                    gapValue=gap_value,
                    gapPercent=gap_percent,
                    year=ref.year,
                    unit=ref.unit,
                )
            )

        # Trier par type de référence dans un ordre logique
        order = {"sector_average": 0, "csrd": 1, "cbam": 2, "net_zero": 3, "sbti": 4}
        items.sort(key=lambda x: order.get(x.referenceType, 99))

        return BenchmarkResponse(
            sector=sector,
            companyTotalEmissions=round(company_total, 2),
            items=items,
        )
