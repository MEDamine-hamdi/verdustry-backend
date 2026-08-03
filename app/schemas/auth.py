from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
from app.core.password_policy import validate_password_strength


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    captcha_token: str
    otp_code: Optional[str] = None


class LoginUser(BaseModel):
    id: str
    email: EmailStr
    name: Optional[str] = None
    role: str
    companyId: Optional[str] = None
    otpEnabled: bool = False
    emailVerified: bool = True


class LoginResponse(BaseModel):
    access_token: Optional[str] = None
    user: Optional[LoginUser] = None
    otpRequired: bool = False


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def check_new_password(cls, v: str) -> str:
        return validate_password_strength(v)


class VerifyEmailRequest(BaseModel):
    token: str


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class RequestOtpRequest(BaseModel):
    email: EmailStr


class VerifyOtpRequest(BaseModel):
    email: EmailStr
    code: str


class ConfirmOtpEnableRequest(BaseModel):
    code: str


class GoogleLoginRequest(BaseModel):
    idToken: str