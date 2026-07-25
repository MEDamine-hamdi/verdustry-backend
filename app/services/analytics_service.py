from typing import Optional, List
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.emission import Emission
from app.models.site import Site
from app.schemas.analytics import (
    EmissionAggregateItem,
    EmissionAggregateResponse,
    TrendPoint,
    TrendResponse,
    TopEmitterItem,
    TopEmittersResponse,
)

VALID_GROUP_BY = {"site", "scope", "category", "period"}


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def aggregate(
        self,
        company_id: int,
        group_by: str,
        scope: Optional[int] = None,
        site_id: Optional[int] = None,
        period_from: Optional[str] = None,
        period_to: Optional[str] = None,
    ) -> EmissionAggregateResponse:
        if group_by not in VALID_GROUP_BY:
            group_by = "scope"

        query = self.db.query(Emission).filter(Emission.company_id == company_id)
        if scope is not None:
            query = query.filter(Emission.scope == scope)
        if site_id is not None:
            query = query.filter(Emission.site_id == site_id)
        if period_from is not None:
            query = query.filter(Emission.period >= period_from)
        if period_to is not None:
            query = query.filter(Emission.period <= period_to)

        emissions = query.all()

        groups: dict = defaultdict(float)
        for e in emissions:
            if group_by == "site":
                site = self.db.query(Site).filter(Site.id == e.site_id).first()
                key = site.name if site else "Non assigné"
            elif group_by == "scope":
                key = f"Scope {e.scope}"
            elif group_by == "category":
                key = e.category or "Non catégorisé"
            else:  # period
                key = e.period
            groups[key] += e.value

        total = sum(groups.values())
        items = [
            EmissionAggregateItem(key=k, totalValue=round(v, 2))
            for k, v in sorted(groups.items(), key=lambda x: -x[1])
        ]

        return EmissionAggregateResponse(groupBy=group_by, items=items, totalValue=round(total, 2))

    def trend(self, company_id: int, scope: Optional[int] = None) -> TrendResponse:
        query = self.db.query(Emission).filter(Emission.company_id == company_id)
        if scope is not None:
            query = query.filter(Emission.scope == scope)

        emissions = query.all()

        by_period: dict = defaultdict(float)
        for e in emissions:
            by_period[e.period] += e.value

        sorted_periods = sorted(by_period.keys())
        points = [TrendPoint(period=p, value=round(by_period[p], 2)) for p in sorted_periods]

        change_percent = None
        if len(points) >= 2:
            prev = points[-2].value
            curr = points[-1].value
            if prev != 0:
                change_percent = round(((curr - prev) / prev) * 100, 2)

        return TrendResponse(points=points, changePercent=change_percent)

    def top_emitters(self, company_id: int, limit: int = 5) -> TopEmittersResponse:
        emissions = self.db.query(Emission).filter(Emission.company_id == company_id).all()

        by_category: dict = defaultdict(float)
        for e in emissions:
            key = e.category or "Non catégorisé"
            by_category[key] += e.value

        total = sum(by_category.values())
        sorted_items = sorted(by_category.items(), key=lambda x: -x[1])[:limit]

        items = [
            TopEmitterItem(
                category=k,
                totalValue=round(v, 2),
                percentOfTotal=round((v / total * 100) if total > 0 else 0, 1),
            )
            for k, v in sorted_items
        ]

        return TopEmittersResponse(items=items)