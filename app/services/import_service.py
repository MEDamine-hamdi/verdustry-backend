import io
from typing import BinaryIO
import pandas as pd
from sqlalchemy.orm import Session

from app.models.emission import Emission
from app.models.import_log import ImportLog
from app.models.data_source import DataSource
from app.repositories.import_log_repository import ImportLogRepository

REQUIRED_COLUMNS = {"scope", "value", "unit", "period"}
VALID_SCOPES = {1, 2, 3}


class ImportService:
    def __init__(self, db: Session):
        self.db = db
        self.import_log_repo = ImportLogRepository(db)

    def _read_file(self, file: BinaryIO, filename: str) -> pd.DataFrame:
        content = file.read()
        if filename.endswith(".csv"):
            return pd.read_csv(io.BytesIO(content))
        elif filename.endswith(".xlsx") or filename.endswith(".xls"):
            return pd.read_excel(io.BytesIO(content))
        else:
            raise ValueError("Format de fichier non supporté (attendu: .csv, .xlsx, .xls)")

    def import_emissions(
        self,
        file: BinaryIO,
        filename: str,
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
            df = self._read_file(file, filename)
        except Exception as e:
            log.status = "failed"
            log.error_message = str(e)
            self.import_log_repo.update(log)
            return log

        df.columns = [str(c).strip().lower() for c in df.columns]
        missing = REQUIRED_COLUMNS - set(df.columns)
        if missing:
            log.status = "failed"
            log.error_message = f"Colonnes manquantes: {', '.join(missing)}"
            self.import_log_repo.update(log)
            return log

        total = len(df)
        imported = 0
        failed = 0
        errors = []

        for idx, row in df.iterrows():
            try:
                scope = int(row["scope"])
                if scope not in VALID_SCOPES:
                    raise ValueError(f"scope invalide: {scope} (doit être 1, 2 ou 3)")

                value = float(row["value"])
                unit = str(row["unit"]).strip()
                period = str(row["period"]).strip()
                category = str(row["category"]).strip() if "category" in df.columns and pd.notna(row.get("category")) else None

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
                errors.append(f"Ligne {idx + 2}: {str(e)}")

        self.db.commit()

        log.rows_total = total
        log.rows_imported = imported
        log.rows_failed = failed
        log.status = "success" if failed == 0 else ("partial" if imported > 0 else "failed")
        if errors:
            log.error_message = "; ".join(errors[:10])  # limite pour ne pas exploser la colonne
        self.import_log_repo.update(log)

        return log