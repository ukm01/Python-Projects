import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from jose import JWTError
from sqlalchemy.orm import Session

from app.config import settings
from app.models.password_reset_model import PasswordResetOTP
from app.repositories.user_repository import get_user_by_email
from app.security.jwt_handler import (
    create_password_reset_token,
    decode_password_reset_token,
)
from app.security.password_handler import hash_password
from app.services.email_service import (
    EmailConfigurationError,
    EmailDeliveryError,
    ensure_email_configured,
    send_password_reset_otp,
)


RESET_REQUEST_MESSAGE = (
    "If an active account exists for that email, a verification code has been sent."
)


def request_password_reset(db: Session, email: str) -> dict[str, str]:
    try:
        ensure_email_configured()
    except EmailConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Password reset email is not configured",
        ) from exc

    user = get_user_by_email(db, email)

    if not user or not user.is_active:
        return {"message": RESET_REQUEST_MESSAGE}

    now = datetime.now(timezone.utc)

    (
        db.query(PasswordResetOTP)
        .filter(
            PasswordResetOTP.user_id == user.id,
            PasswordResetOTP.used_at.is_(None),
        )
        .update({"used_at": now}, synchronize_session=False)
    )

    otp = f"{secrets.randbelow(1_000_000):06d}"
    reset_record = PasswordResetOTP(
        user_id=user.id,
        otp_digest=_digest_otp(otp),
        expires_at=now
        + timedelta(minutes=settings.PASSWORD_RESET_OTP_EXPIRE_MINUTES),
    )
    db.add(reset_record)
    db.commit()

    try:
        send_password_reset_otp(
            recipient_email=user.email,
            recipient_name=user.name,
            otp=otp,
        )
    except EmailDeliveryError as exc:
        reset_record.used_at = datetime.now(timezone.utc)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Password reset email could not be sent",
        ) from exc

    return {"message": RESET_REQUEST_MESSAGE}


def verify_password_reset_otp(
    db: Session,
    email: str,
    otp: str,
) -> dict[str, str]:
    user = get_user_by_email(db, email)

    if not user or not user.is_active:
        raise _invalid_otp_error()

    reset_record = (
        db.query(PasswordResetOTP)
        .filter(
            PasswordResetOTP.user_id == user.id,
            PasswordResetOTP.used_at.is_(None),
        )
        .order_by(PasswordResetOTP.created_at.desc())
        .first()
    )

    now = datetime.now(timezone.utc)

    if (
        not reset_record
        or reset_record.expires_at <= now
        or reset_record.attempts >= settings.PASSWORD_RESET_MAX_ATTEMPTS
    ):
        raise _invalid_otp_error()

    if not hmac.compare_digest(reset_record.otp_digest, _digest_otp(otp)):
        reset_record.attempts += 1
        db.commit()
        raise _invalid_otp_error()

    reset_record.verified_at = now
    db.commit()

    return {
        "reset_token": create_password_reset_token(
            email=user.email,
            otp_id=reset_record.id,
        )
    }


def confirm_password_reset(
    db: Session,
    reset_token: str,
    password: str,
) -> dict[str, str]:
    try:
        payload = decode_password_reset_token(reset_token)
        email = payload.get("sub")
        otp_id = int(payload.get("otp_id"))
    except (JWTError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The password reset session is invalid or expired",
        ) from exc

    user = get_user_by_email(db, email)
    reset_record = (
        db.query(PasswordResetOTP)
        .filter(
            PasswordResetOTP.id == otp_id,
            PasswordResetOTP.user_id == (user.id if user else -1),
        )
        .first()
    )
    now = datetime.now(timezone.utc)

    if (
        not user
        or not reset_record
        or reset_record.verified_at is None
        or reset_record.used_at is not None
        or reset_record.expires_at <= now
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The password reset session is invalid or expired",
        )

    user.hashed_password = hash_password(password)
    reset_record.used_at = now
    db.commit()

    return {"message": "Password updated successfully"}


def _digest_otp(otp: str) -> str:
    return hmac.new(
        settings.JWT_SECRET_KEY.encode("utf-8"),
        otp.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def _invalid_otp_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="The verification code is invalid or expired",
    )
