from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.models.emission import Emission
from app.models.import_log import ImportLog
from app.repositories.import_log_repository import ImportLogRepository
from app.core.ssrf_guard import validate_db_host_safe, SSRFError

REQUIRED_COLUMNS = {"scope", "value", "unit", "period"}
VALID_SCOPES = {1, 2, 3}


class SqlImportService:
    def __init__(self, db: Session):
        self.db = db
        self.import_log_repo = ImportLogRepository(db)

    def import_emissions_from_sql(
        self,
        connection_url: str,
        query: str,
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

        normalized_query = query.strip().lower()
        if not normalized_query.startswith("select"):
            log.status = "failed"
            log.error_message = "Seules les requêtes SELECT sont autorisées."
            self.import_log_repo.update(log)
            return log

        try:
            validate_db_host_safe(connection_url)
        except SSRFError as e:
            log.status = "failed"
            log.error_message = f"Connexion non autorisée: {str(e)}"
            self.import_log_repo.update(log)
            return log

        try:
            external_engine = create_engine(connection_url)
            with external_engine.connect() as conn:
                result = conn.execute(text(query))
                columns = [c.lower() for c in result.keys()]
                rows = result.fetchall()
        except Exception as e:
            log.status = "failed"
            log.error_message = f"Erreur de connexion/requête: {str(e)}"
            self.import_log_repo.update(log)
            return log

        missing = REQUIRED_COLUMNS - set(columns)
        if missing:
            log.status = "failed"
            log.error_message = f"Colonnes manquantes dans le résultat SQL: {', '.join(missing)}"
            self.import_log_repo.update(log)
            return log

        total = len(rows)
        imported = 0
        failed = 0
        errors = []
        for idx, row in enumerate(rows):
            row_dict = dict(zip(columns, row))
            try:
                scope = int(row_dict["scope"])
                if scope not in VALID_SCOPES:
                    raise ValueError(f"scope invalide: {scope}")
                value = float(row_dict["value"])
                unit = str(row_dict["unit"]).strip()
                period = str(row_dict["period"]).strip()
                category = str(row_dict.get("category")) if row_dict.get("category") else None
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
                errors.append(f"Ligne {idx + 1}: {str(e)}")

        self.db.commit()
        log.rows_total = total
        log.rows_imported = imported
        log.rows_failed = failed
        log.status = "success" if failed == 0 else ("partial" if imported > 0 else "failed")
        if errors:
            log.error_message = "; ".join(errors[:10])
        self.import_log_repo.update(log)
        return log