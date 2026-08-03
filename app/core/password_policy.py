import re

MIN_LENGTH = 8


def validate_password_strength(password: str) -> str:
    if len(password) < MIN_LENGTH:
        raise ValueError(f"Le mot de passe doit contenir au moins {MIN_LENGTH} caractères.")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Le mot de passe doit contenir au moins une majuscule.")
    if not re.search(r"[a-z]", password):
        raise ValueError("Le mot de passe doit contenir au moins une minuscule.")
    if not re.search(r"[0-9]", password):
        raise ValueError("Le mot de passe doit contenir au moins un chiffre.")
    return password
