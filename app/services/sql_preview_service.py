from typing import List, Dict, Any

from sqlalchemy import create_engine, text

from app.core.ssrf_guard import validate_db_host_safe, SSRFError


class SqlPreviewError(Exception):
    pass


class SqlPreviewService:
    """Exécute une requête SELECT en lecture seule et retourne les lignes brutes,
    sans écrire dans aucune table. Utilisé pour pré-remplir le calculateur Bilan carbone."""

    def run_query(self, connection_url: str, query: str) -> List[Dict[str, Any]]:
        normalized_query = query.strip().lower()
        if not normalized_query.startswith("select"):
            raise SqlPreviewError("Seules les requêtes SELECT sont autorisées.")

        try:
            validate_db_host_safe(connection_url)
        except SSRFError as e:
            raise SqlPreviewError(f"Connexion non autorisée: {str(e)}")

        try:
            engine = create_engine(connection_url)
            with engine.connect() as conn:
                result = conn.execute(text(query))
                columns = [c.lower() for c in result.keys()]
                rows = result.fetchall()
        except Exception as e:
            raise SqlPreviewError(f"Erreur de connexion/requête: {str(e)}")

        return [dict(zip(columns, row)) for row in rows]