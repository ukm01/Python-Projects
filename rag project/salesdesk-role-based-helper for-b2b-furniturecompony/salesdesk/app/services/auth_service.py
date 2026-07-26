from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.user_repository import get_user_by_email, create_user
from app.security.password_handler import hash_password, verify_password
from app.security.jwt_handler import create_access_token


def create_admin_user(
    db: Session,
    name: str,
    email: str,
    password: str,
    department: str | None = "IT"
):
    existing_user = get_user_by_email(db, email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    hashed_password = hash_password(password)

    user = create_user(
        db=db,
        name=name,
        email=email,
        hashed_password=hashed_password,
        role="admin",
        department=department,
        is_active=True
    )

    return user


def login_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    is_password_valid = verify_password(password, user.hashed_password)

    if not is_password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        data={
            "sub": user.email,
            "role": user.role,
            "user_id": user.id
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "department": user.department
        }
    }