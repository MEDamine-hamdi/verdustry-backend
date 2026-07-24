from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None
    role: str
    companyId: Optional[str] = None
    isActive: Optional[bool] = Field(default=None, alias="isActive")

    model_config = ConfigDict(populate_by_name=True)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = None
    companyId: Optional[str] = None
    isActive: Optional[bool] = Field(default=None, alias="isActive")

    model_config = ConfigDict(populate_by_name=True)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    email: EmailStr
    name: Optional[str] = None
    role: str
    isActive: bool
    companyId: Optional[str] = None