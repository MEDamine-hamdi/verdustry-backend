from fastapi import HTTPException, status

from app.models.user import User


def enforce_company_access(current_user: User, company_id: int) -> None:
    """
    Vérifie que l'utilisateur a le droit d'accéder aux données de cette entreprise.
    - ADMIN : accès à toutes les entreprises.
    - Autres rôles : uniquement leur propre entreprise (company_id du compte).
    """
    if current_user.role.name == "ADMIN":
        return

    if current_user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas accès aux données de cette entreprise.",
        )