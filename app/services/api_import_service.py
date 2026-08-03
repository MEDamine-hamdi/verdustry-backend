from typing import Optional
import httpx
from sqlalchemy.orm import Session
from app.models.emission import Emission
from app.models.import_log import ImportLog
from app.repositories.import_log_repository import ImportLogRepository
from app.core.ssrf_guard import validate_url_safe, SSRFError

REQUIRED_FIELDS = {"scope", "value", "unit", "period"}
VALID_SCOPES = {1, 2, 3}


class ApiImportService:
    def __init__(self, db: Session):
        self.db = db
        self.import_log_repo = ImportLogRepository(db)

    def import_emissions_from_api(
        self,
        url: str,
        auth_header: Optional[str],
        company_id: int,
        user_id: int,
        data_source_id: int,
    ) -> ImportLog:
        log = ImportLog(
            data_source_id=data_source_id,
            company_id=company_id,
            imported_by_id=user_id,
            status="pending",
        )
        log = self.import_log_repo.create(log)

        try:
            validate_url_safe(url)
        except SSRFError as e:
            log.status = "failed"
            log.error_message = f"URL non autorisée: {str(e)}"
            self.import_log_repo.update(log)
            return log

        headers = {}
        if auth_header:
            headers["Authorization"] = auth_header

        try:
            response = httpx.get(
                url,
                headers=headers,
                timeout=15.0,
                follow_redirects=False,
            )
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            log.status = "failed"
            log.error_message = f"Erreur d'appel API: {str(e)}"
            self.import_log_repo.update(log)
            return log

        if isinstance(data, dict):
            rows = data.get("data") or data.get("results") or data.get("items")
            if rows is None:
                log.status = "failed"
                log.error_message = "Réponse API: format non reconnu (attendu une liste, ou un objet avec 'data'/'results'/'items')"
                self.import_log_repo.update(log)
                return log
        elif isinstance(data, list):
            rows = data
        else:
            log.status = "failed"
            log.error_message = "Réponse API: format non reconnu"
            self.import_log_repo.update(log)
            return log

        total = len(rows)
        imported = 0
        failed = 0
        errors = []
        for idx, row in enumerate(rows):
            try:
                row_lower = {str(k).lower(): v for k, v in row.items()}
                missing = REQUIRED_FIELDS - set(row_lower.keys())
                if missing:
                    raise ValueError(f"champs manquants: {', '.join(missing)}")
                scope = int(row_lower["scope"])
                if scope not in VALID_SCOPES:
                    raise ValueError(f"scope invalide: {scope}")
                value = float(row_lower["value"])
                unit = str(row_lower["unit"]).strip()
                period = str(row_lower["period"]).strip()
                category = str(row_lower.get("category")) if row_lower.get("category") else None
                emission = Emission(
                    company_id=company_id,
                    scope=scope,
                    category=category,
                    value=value,
                    unit=unit,
                    period=period,
                    import_log_id=log.id,
                )
                self.db.add(emission)
                imported += 1
            except Exception as e:
                failed += 1
                errors.append(f"Élément {idx + 1}: {str(e)}")

        self.db.commit()
        log.rows_total = total
        log.rows_imported = imported
        log.rows_failed = failed
        log.status = "success" if failed == 0 else ("partial" if imported > 0 else "failed")
        if errors:
            log.error_message = "; ".join(errors[:10])
        self.import_log_repo.update(log)
        return log