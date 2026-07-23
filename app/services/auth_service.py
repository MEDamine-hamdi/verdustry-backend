from typing import Optional
from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from app.utils.password import verify_password
from app.utils.jwt import create_access_token
from app.models.user import User


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)

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