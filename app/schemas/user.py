from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator
from app.core.password_policy import validate_password_strength


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None
    role: str
    companyId: Optional[str] = None
    isActive: Optional[bool] = Field(default=None, alias="isActive")
    model_config = ConfigDict(populate_by_name=True)

    @field_validator("password")
    @classmethod
    def check_password(cls, v: str) -> str:
        return validate_password_strength(v)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = None
    companyId: Optional[str] = None
    isActive: Optional[bool] = Field(default=None, alias="isActive")
    model_config = ConfigDict(populate_by_name=True)

    @field_validator("password")
    @classmethod
    def check_password(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_password_strength(v)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    email: EmailStr
    name: Optional[str] = None
    role: str
    isActive: bool
    companyId: Optional[str] = None