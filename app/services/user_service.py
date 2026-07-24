from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories.user_repository import UserRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.company_repository import CompanyRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.utils.password import hash_password
from app.services.auth_service import AuthService


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)
        self.role_repository = RoleRepository(db)
        self.company_repository = CompanyRepository(db)
        self.auth_service = AuthService(db)

    def _to_response(self, user: User) -> UserResponse:
        return UserResponse(
            id=str(user.id),
            email=user.email,
            name=user.full_name,
            role=user.role.name,
            isActive=user.is_active,
            companyId=str(user.company_id) if user.company_id else None,
        )

    def get_user(self, user_id: int) -> UserResponse:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return self._to_response(user)

    def get_all_users(self) -> List[UserResponse]:
        return [self._to_response(u) for u in self.user_repository.get_all()]

    def create_user(self, user_data: UserCreate) -> UserResponse:
        existing_user = self.user_repository.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        role = self.role_repository.get_by_name(user_data.role)
        if not role:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")

        company_id = None
        if role.name != "ADMIN":
            if not user_data.companyId:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="companyId is required for non-ADMIN users",
                )
            company = self.company_repository.get_by_id(int(user_data.companyId))
            if not company:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid companyId")
            company_id = company.id

        new_user = User(
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            full_name=user_data.name,
            role_id=role.id,
            company_id=company_id,
            is_active=user_data.isActive if user_data.isActive is not None else True,
            email_verified=False,
        )
        created = self.user_repository.create(new_user)
        self.auth_service.send_email_verification(created)
        return self._to_response(created)

    def update_user(self, user_id: int, user_data: UserUpdate) -> UserResponse:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if user_data.email is not None:
            user.email = user_data.email
        if user_data.name is not None:
            user.full_name = user_data.name
        if user_data.role is not None:
            role = self.role_repository.get_by_name(user_data.role)
            if not role:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")
            user.role_id = role.id
        if user_data.password is not None:
            user.hashed_password = hash_password(user_data.password)
        if user_data.isActive is not None:
            user.is_active = user_data.isActive
        if user_data.companyId is not None:
            company = self.company_repository.get_by_id(int(user_data.companyId))
            if not company:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid companyId")
            user.company_id = company.id

        updated = self.user_repository.update(user)
        return self._to_response(updated)

    def delete_user(self, user_id: int) -> None:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        self.user_repository.delete(user)