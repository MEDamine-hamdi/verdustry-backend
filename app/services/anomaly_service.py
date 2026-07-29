"""Anomaly detection for company emission time series."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Tuple

import numpy as np
from sqlalchemy.orm import Session

from app.models.emission import Emission
from app.schemas.anomaly import AnomalyAlert, AnomalyResponse, AnomalySummary

ZSCORE_MIN_POINTS = 3
ZSCORE_FLAG = 2.0
ZSCORE_HIGH = 3.0
ISOLATION_MIN_POINTS = 5


class AnomalyService:
    def __init__(self, db: Session):
        self.db = db

    def detect(self, company_id: int) -> AnomalyResponse:
        emissions = (
            self.db.query(Emission).filter(Emission.company_id == company_id).all()
        )
        if not emissions:
            return AnomalyResponse(
                alerts=[],
                summary=AnomalySummary(high=0, medium=0, low=0, total=0),
            )

        totals, scopes = self._build_series(emissions)
        periods = sorted(totals.keys())

        alerts: List[AnomalyAlert] = []
        alerts.extend(self._detect_spikes(periods, totals))
        alerts.extend(self._detect_inconsistencies(periods, totals, scopes))

        # Newest periods first
        alerts.sort(key=lambda a: a.period, reverse=True)

        summary = AnomalySummary(
            high=sum(1 for a in alerts if a.severity == "high"),
            medium=sum(1 for a in alerts if a.severity == "medium"),
            low=sum(1 for a in alerts if a.severity == "low"),
            total=len(alerts),
        )

        return AnomalyResponse(alerts=alerts, summary=summary)

    def _build_series(
        self, emissions: List[Emission]
    ) -> Tuple[Dict[str, float], Dict[str, Dict[int, float]]]:
        totals: Dict[str, float] = defaultdict(float)
        scopes: Dict[str, Dict[int, float]] = defaultdict(lambda: defaultdict(float))
        for e in emissions:
            totals[e.period] += e.value
            scopes[e.period][e.scope] += e.value
        return dict(totals), {p: dict(s) for p, s in scopes.items()}

    def _detect_spikes(
        self, periods: List[str], totals: Dict[str, float]
    ) -> List[AnomalyAlert]:
        if len(periods) < ZSCORE_MIN_POINTS:
            return []

        values = np.array([totals[p] for p in periods], dtype=float)
        mean = float(np.mean(values))
        std = float(np.std(values, ddof=0))
        if std == 0:
            return []

        alerts: List[AnomalyAlert] = []
        for period, value in zip(periods, values):
            z = float((value - mean) / std)
            abs_z = abs(z)
            if abs_z < ZSCORE_FLAG:
                continue

            severity = "high" if abs_z >= ZSCORE_HIGH else "medium"
            direction = "hausse" if z > 0 else "baisse"

            alerts.append(
                AnomalyAlert(
                    type="unusual_spike",
                    severity=severity,
                    period=period,
                    message=(
                        f"{direction.capitalize()} inhabituelle des émissions "
                        f"sur {period} (z-score={z:.2f})."
                    ),
                    value=round(float(value), 2),
                    score=round(abs_z, 3),
                    details={
                        "zScore": round(z, 3),
                        "mean": round(mean, 2),
                        "std": round(std, 2),
                        "direction": "up" if z > 0 else "down",
                    },
                )
            )
        return alerts

    def _detect_inconsistencies(
        self,
        periods: List[str],
        totals: Dict[str, float],
        scopes: Dict[str, Dict[int, float]],
    ) -> List[AnomalyAlert]:
        if len(periods) < ISOLATION_MIN_POINTS:
            return []

        try:
            from sklearn.ensemble import IsolationForest
        except ImportError:
            return []

        matrix = []
        for p in periods:
            total = totals[p]
            s1 = scopes.get(p, {}).get(1, 0.0)
            s2 = scopes.get(p, {}).get(2, 0.0)
            s3 = scopes.get(p, {}).get(3, 0.0)
            # Use shares + total so mix anomalies are detectable
            if total > 0:
                matrix.append([total, s1 / total, s2 / total, s3 / total])
            else:
                matrix.append([0.0, 0.0, 0.0, 0.0])

        X = np.array(matrix, dtype=float)
        model = IsolationForest(
            n_estimators=100,
            contamination="auto",
            random_state=42,
        )
        labels = model.fit_predict(X)
        scores = model.decision_function(X)

        alerts: List[AnomalyAlert] = []
        for period, label, score, row in zip(periods, labels, scores, matrix):
            if label != -1:
                continue

            # IsolationForest: lower decision_function = more anomalous
            anomaly_score = float(-score)
            severity = "high" if anomaly_score >= 0.15 else "medium"
            total, r1, r2, r3 = row

            alerts.append(
                AnomalyAlert(
                    type="indicator_inconsistency",
                    severity=severity,
                    period=period,
                    message=(
                        f"Répartition des scopes inhabituelle sur {period} "
                        f"(Isolation Forest)."
                    ),
                    value=round(float(total), 2),
                    score=round(anomaly_score, 3),
                    details={
                        "scope1Share": round(float(r1), 3),
                        "scope2Share": round(float(r2), 3),
                        "scope3Share": round(float(r3), 3),
                        "isolationScore": round(float(score), 3),
                    },
                )
            )
        return alerts