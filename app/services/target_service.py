from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories.target_repository import TargetRepository
from app.models.target import Target
from app.schemas.target import TargetCreate, TargetUpdate, TargetResponse


class TargetService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TargetRepository(db)

    def _to_response(self, target: Target) -> TargetResponse:
        return TargetResponse(
            id=str(target.id),
            name=target.name,
            metric=target.metric,
            baselineValue=target.baseline_value,
            baselineYear=target.baseline_year,
            targetValue=target.target_value,
            targetYear=target.target_year,
            deadline=target.deadline,
            companyId=str(target.company_id),
        )

    def get_all(self, company_id: int) -> List[TargetResponse]:
        return [self._to_response(t) for t in self.repo.get_all_by_company(company_id)]

    def create(self, data: TargetCreate) -> TargetResponse:
        target = Target(
            name=data.name,
            metric=data.metric,
            baseline_value=data.baselineValue,
            baseline_year=data.baselineYear,
            target_value=data.targetValue,
            target_year=data.targetYear,
            deadline=data.deadline,
            company_id=int(data.companyId),
        )
        created = self.repo.create(target)
        return self._to_response(created)

    def update(self, target_id: int, data: TargetUpdate) -> TargetResponse:
        target = self.repo.get_by_id(target_id)
        if not target:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target not found")
        if data.name is not None:
            target.name = data.name
        if data.metric is not None:
            target.metric = data.metric
        if data.baselineValue is not None:
            target.baseline_value = data.baselineValue
        if data.baselineYear is not None:
            target.baseline_year = data.baselineYear
        if data.targetValue is not None:
            target.target_value = data.targetValue
        if data.targetYear is not None:
            target.target_year = data.targetYear
        if data.deadline is not None:
            target.deadline = data.deadline
        updated = self.repo.update(target)
        return self._to_response(updated)

    def delete(self, target_id: int) -> None:
        target = self.repo.get_by_id(target_id)
        if not target:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target not found")
        self.repo.delete(target)