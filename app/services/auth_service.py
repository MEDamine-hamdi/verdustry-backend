from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories.user_repository import UserRepository
from app.services.token_service import TokenService
from app.utils.password import verify_password, hash_password
from app.utils.jwt import create_access_token
from app.utils.email import send_email
from app.models.user import User
from app.core.config import settings


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)
        self.token_service = TokenService(db)

    def authenticate(self, email: str, password: str) -> Optional[User]:
        user = self.user_repository.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user

    def create_token(self, user: User) -> str:
        return create_access_token(data={"sub": str(user.id)})

    def login_flow(self, email: str, password: str, otp_code: Optional[str] = None) -> Optional[dict]:
        user = self.authenticate(email, password)
        if not user:
            return None

        if not user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email not verified. Please check your inbox to verify your email.",
            )

        if user.otp_enabled:
            if not otp_code:
                self.request_otp(email)
                return {"otpRequired": True, "access_token": None, "user": None}
            valid = self.verify_otp(email, otp_code)
            if not valid:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired code")

        token = self.create_token(user)
        return {"otpRequired": False, "access_token": token, "user": user}

    def request_password_reset(self, email: str) -> None:
        user = self.user_repository.get_by_email(email)
        if not user:
            return

        code = self.token_service.create_reset_token(user.id)
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={code}"

        send_email(
            to_email=user.email,
            subject="Réinitialisation de votre mot de passe — Verdustry",
            body=f"""
                <h2>Réinitialisation de mot de passe</h2>
                <p>Cliquez sur le lien ci-dessous pour réinitialiser votre mot de passe (valide 30 minutes) :</p>
                <p><a href="{reset_link}">{reset_link}</a></p>
            """,
        )

    def reset_password(self, token: str, new_password: str) -> None:
        record = self.token_service.validate_token(token, "password_reset")
        if not record:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

        user = self.user_repository.get_by_id(record.user_id)
        user.hashed_password = hash_password(new_password)
        self.user_repository.update(user)
        self.token_service.mark_used(record)

    def send_email_verification(self, user: User) -> None:
        code = self.token_service.create_email_verification_code(user.id)
        verify_link = f"{settings.FRONTEND_URL}/verify-email?token={code}"

        send_email(
            to_email=user.email,
            subject="Vérifiez votre adresse email — Verdustry",
            body=f"""
                <h2>Bienvenue sur Verdustry</h2>
                <p>Cliquez sur le lien ci-dessous pour vérifier votre adresse email :</p>
                <p><a href="{verify_link}">{verify_link}</a></p>
            """,
        )

    def resend_verification(self, email: str) -> None:
        user = self.user_repository.get_by_email(email)
        if not user or user.email_verified:
            return
        self.send_email_verification(user)

    def verify_email(self, token: str) -> None:
        record = self.token_service.validate_token(token, "email_verification")
        if not record:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

        user = self.user_repository.get_by_id(record.user_id)
        user.email_verified = True
        self.user_repository.update(user)
        self.token_service.mark_used(record)

    def request_otp(self, email: str) -> None:
        user = self.user_repository.get_by_email(email)
        if not user:
            return

        code = self.token_service.create_otp(user.id)

        send_email(
            to_email=user.email,
            subject="Votre code de vérification — Verdustry",
            body=f"""
                <h2>Code de vérification</h2>
                <p>Votre code à usage unique (valide 10 minutes) :</p>
                <h1 style="letter-spacing:4px;">{code}</h1>
            """,
        )

    def verify_otp(self, email: str, code: str) -> bool:
        user = self.user_repository.get_by_email(email)
        if not user:
            return False

        record = self.token_service.validate_token(code, "otp")
        if not record or record.user_id != user.id:
            return False

        self.token_service.mark_used(record)
        return True

    def request_enable_otp(self, user: User) -> None:
        code = self.token_service.create_otp(user.id)
        send_email(
            to_email=user.email,
            subject="Activation de la double authentification — Verdustry",
            body=f"""
                <h2>Activation de la double authentification</h2>
                <p>Votre code de confirmation (valide 10 minutes) :</p>
                <h1 style="letter-spacing:4px;">{code}</h1>
            """,
        )

    def confirm_enable_otp(self, user: User, code: str) -> None:
        valid = self.verify_otp(user.email, code)
        if not valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired code")
        user.otp_enabled = True
        self.user_repository.update(user)

    def disable_otp(self, user: User) -> None:
        user.otp_enabled = False
        self.user_repository.update(user)