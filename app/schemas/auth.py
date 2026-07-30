from typing import Optional
from pydantic import BaseModel, EmailStr


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