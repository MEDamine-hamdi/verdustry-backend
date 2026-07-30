from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import get_current_user, verify_captcha
from app.services.auth_service import AuthService
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    LoginUser,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
    ResendVerificationRequest,
    RequestOtpRequest,
    VerifyOtpRequest,
    ConfirmOtpEnableRequest,
GoogleLoginRequest,
)
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Auth"])


def _to_login_user(user: User) -> LoginUser:
    return LoginUser(
        id=str(user.id),
        email=user.email,
        name=user.full_name,
        role=user.role.name,
        companyId=str(user.company_id) if user.company_id else None,
        otpEnabled=user.otp_enabled,
        emailVerified=user.email_verified,
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    if not credentials.otp_code:
        captcha_ok = await verify_captcha(credentials.captcha_token, request.client.host if request.client else None)
        if not captcha_ok:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vérification captcha échouée.",
        )

    auth_service = AuthService(db)
    result = auth_service.login_flow(credentials.email, credentials.password, credentials.otp_code)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if result["otpRequired"]:
        return LoginResponse(otpRequired=True)
    return LoginResponse(
        access_token=result["access_token"],
        user=_to_login_user(result["user"]),
        otpRequired=False,
    )

@router.post("/google", response_model=LoginResponse)
def login_with_google(
    data: GoogleLoginRequest,
    db: Session = Depends(get_db),
):
    auth_service = AuthService(db)
    result = auth_service.login_with_google(data.idToken)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ce compte Google n'est pas reconnu. Contactez votre administrateur.",
        )
    return LoginResponse(
        access_token=result["access_token"],
        user=_to_login_user(result["user"]),
        otpRequired=False,
    )
@router.get("/me", response_model=LoginUser)
def get_me(current_user: User = Depends(get_current_user)):
    return _to_login_user(current_user)


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    auth_service.request_password_reset(data.email)
    return {"ok": True, "message": "If this email exists, a reset link has been sent."}


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    auth_service.reset_password(data.token, data.new_password)
    return {"ok": True, "message": "Password has been reset."}


@router.post("/verify-email")
def verify_email(data: VerifyEmailRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    auth_service.verify_email(data.token)
    return {"ok": True, "message": "Email verified."}


@router.post("/resend-verification")
def resend_verification(data: ResendVerificationRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    auth_service.resend_verification(data.email)
    return {"ok": True, "message": "If this email exists and is not verified, a new link has been sent."}


@router.post("/request-otp")
def request_otp(data: RequestOtpRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    auth_service.request_otp(data.email)
    return {"ok": True, "message": "If this email exists, a code has been sent."}


@router.post("/verify-otp")
def verify_otp(data: VerifyOtpRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    valid = auth_service.verify_otp(data.email, data.code)
    if not valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired code")
    return {"ok": True, "message": "Code verified."}


@router.post("/otp/enable/request")
def request_enable_otp(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    auth_service = AuthService(db)
    auth_service.request_enable_otp(current_user)
    return {"ok": True, "message": "Code sent."}


@router.post("/otp/enable/confirm")
def confirm_enable_otp(
    data: ConfirmOtpEnableRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    auth_service = AuthService(db)
    auth_service.confirm_enable_otp(current_user, data.code)
    return {"ok": True, "message": "Two-factor authentication enabled."}


@router.post("/otp/disable")
def disable_otp(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    auth_service = AuthService(db)
    auth_service.disable_otp(current_user)
    return {"ok": True, "message": "Two-factor authentication disabled."}