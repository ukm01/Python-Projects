from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user_model import User
from app.schemas.auth_schema import LoginRequest, LoginResponse
from app.schemas.password_reset_schema import (
    MessageResponse,
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    PasswordResetVerifyRequest,
    PasswordResetVerifyResponse,
)
from app.schemas.user_schema import UserResponse
from app.security.dependencies import get_current_user
from app.security.roles import ACCESS_ROLES
from app.services.auth_service import login_user
from app.services.password_reset_service import (
    confirm_password_reset,
    request_password_reset,
    verify_password_reset_otp,
)


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/login", response_model=LoginResponse)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    return login_user(
        db=db,
        email=request.email,
        password=request.password
    )


@router.post(
    "/password-reset/request",
    response_model=MessageResponse,
)
def request_reset(
    request: PasswordResetRequest,
    db: Session = Depends(get_db),
):
    return request_password_reset(
        db=db,
        email=str(request.email),
    )


@router.post(
    "/password-reset/verify",
    response_model=PasswordResetVerifyResponse,
)
def verify_reset_code(
    request: PasswordResetVerifyRequest,
    db: Session = Depends(get_db),
):
    return verify_password_reset_otp(
        db=db,
        email=str(request.email),
        otp=request.otp,
    )


@router.post(
    "/password-reset/confirm",
    response_model=MessageResponse,
)
def confirm_reset(
    request: PasswordResetConfirmRequest,
    db: Session = Depends(get_db),
):
    return confirm_password_reset(
        db=db,
        reset_token=request.reset_token,
        password=request.password,
    )


@router.post("/token", response_model=LoginResponse)
def swagger_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    return login_user(
        db=db,
        email=form_data.username,
        password=form_data.password
    )


@router.get("/me", response_model=UserResponse)
def get_logged_in_user(
    current_user: User = Depends(get_current_user)
):
    return current_user


@router.get("/roles")
def get_access_roles(
    current_user: User = Depends(get_current_user)
):
    return {
        "roles": list(ACCESS_ROLES)
    }
