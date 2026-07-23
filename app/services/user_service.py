from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories.user_repository import UserRepository
from app.repositories.role_repository import RoleRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.password import hash_password


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)
        self.role_repository = RoleRepository(db)

    def get_user(self, user_id: int) -> User:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user

    def get_all_users(self) -> List[User]:
        return self.user_repository.get_all()

    def create_user(self, user_data: UserCreate) -> User:
        existing_user = self.user_repository.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        role = self.role_repository.get_by_id(user_data.role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role_id",
            )

        new_user = User(
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            full_name=user_data.full_name,
            role_id=user_data.role_id,
        )
        return self.user_repository.create(new_user)

    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        user = self.get_user(user_id)

        if user_data.email is not None:
            user.email = user_data.email
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        if user_data.role_id is not None:
            role = self.role_repository.get_by_id(user_data.role_id)
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid role_id",
                )
            user.role_id = user_data.role_id
        if user_data.is_active is not None:
            user.is_active = user_data.is_active

        return self.user_repository.update(user)

    def delete_user(self, user_id: int) -> None:
        user = self.get_user(user_id)
        self.user_repository.delete(user)