import xmlrpc.client
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.supplier import Supplier
from app.models.import_log import ImportLog
from app.repositories.import_log_repository import ImportLogRepository


class OdooImportService:
    def __init__(self, db: Session):
        self.db = db
        self.import_log_repo = ImportLogRepository(db)

    def _get_uid(self) -> Optional[int]:
        common = xmlrpc.client.ServerProxy(f"{settings.ODOO_URL}/xmlrpc/2/common")
        return common.authenticate(
            settings.ODOO_DB, settings.ODOO_USERNAME, settings.ODOO_API_KEY, {}
        )

    def _fetch_partners(self, uid: int) -> list[dict]:
        models = xmlrpc.client.ServerProxy(f"{settings.ODOO_URL}/xmlrpc/2/object")
        return models.execute_kw(
            settings.ODOO_DB, uid, settings.ODOO_API_KEY,
            "res.partner", "search_read",
            [[["is_company", "=", True]]],
            {"fields": ["name", "country_id"]},
        )

    def import_suppliers(
        self,
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
            uid = self._get_uid()
            if not uid:
                raise ValueError("Échec de l'authentification Odoo (identifiants invalides)")
            partners = self._fetch_partners(uid)
        except Exception as e:
            log.status = "failed"
            log.error_message = f"Connexion Odoo échouée: {str(e)}"
            self.import_log_repo.update(log)
            return log

        total = len(partners)
        imported = 0
        failed = 0
        errors = []

        for partner in partners:
            try:
                name = partner.get("name")
                if not name:
                    raise ValueError("Nom manquant")

                country_id = partner.get("country_id")
                country = country_id[1] if isinstance(country_id, list) else None

                supplier = Supplier(
                    name=name,
                    country=country,
                    sector=None,
                    company_id=company_id,
                )
                self.db.add(supplier)
                imported += 1
            except Exception as e:
                failed += 1
                errors.append(f"Partner id={partner.get('id')}: {str(e)}")

        self.db.commit()

        log.rows_total = total
        log.rows_imported = imported
        log.rows_failed = failed
        log.status = "success" if failed == 0 else ("partial" if imported > 0 else "failed")
        if errors:
            log.error_message = "; ".join(errors[:10])
        self.import_log_repo.update(log)

        return log