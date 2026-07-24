import secrets
import random
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.verification_token import VerificationToken


class TokenService:
    def __init__(self, db: Session):
        self.db = db

    def create_reset_token(self, user_id: int) -> str:
        code = secrets.token_urlsafe(32)
        self._store(user_id, code, "password_reset", minutes=30)
        return code

    def create_email_verification_code(self, user_id: int) -> str:
        code = secrets.token_urlsafe(32)
        self._store(user_id, code, "email_verification", minutes=60 * 24)
        return code

    def create_otp(self, user_id: int) -> str:
        code = f"{random.randint(0, 999999):06d}"
        self._store(user_id, code, "otp", minutes=10)
        return code

    def _store(self, user_id: int, code: str, token_type: str, minutes: int) -> VerificationToken:
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=minutes)
        token = VerificationToken(
            user_id=user_id,
            code=code,
            token_type=token_type,
            expires_at=expires_at,
            used=False,
        )
        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)
        return token

    def validate_token(self, code: str, token_type: str) -> Optional[VerificationToken]:
        token = (
            self.db.query(VerificationToken)
            .filter(
                VerificationToken.code == code,
                VerificationToken.token_type == token_type,
                VerificationToken.used == False,
            )
            .first()
        )
        if not token:
            return None

        expires_at = token.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at < datetime.now(timezone.utc):
            return None

        return token

    def mark_used(self, token: VerificationToken) -> None:
        token.used = True
        self.db.commit()