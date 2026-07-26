from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user_model import User
from app.repositories.user_repository import (
    count_active_admins,
    create_user,
    get_user_by_email,
    get_user_by_id,
    list_users,
)
from app.schemas.user_schema import UserCreateRequest, UserUpdateRequest
from app.security.password_handler import hash_password
from app.security.roles import AccessRole


def get_users(db: Session) -> list[User]:
    return list_users(db)


def create_managed_user(
    db: Session,
    request: UserCreateRequest,
) -> User:
    email = str(request.email)

    if get_user_by_email(db, email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    return create_user(
        db=db,
        name=request.name,
        email=email,
        hashed_password=hash_password(request.password),
        role=request.role.value,
        department=request.department,
        is_active=True,
    )


def update_managed_user(
    db: Session,
    user_id: int,
    request: UserUpdateRequest,
    current_user: User,
) -> User:
    user = _get_user_or_404(db, user_id)
    fields = request.model_fields_set

    if user.email.strip().lower() == settings.PROTECTED_ADMIN_EMAIL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The protected administrator account cannot be updated",
        )

    if user.id == current_user.id:
        changing_role = "role" in fields and request.role != AccessRole.ADMIN
        deactivating = "is_active" in fields and request.is_active is False

        if changing_role or deactivating:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot remove your own admin access",
            )

    removing_active_admin = (
        user.role == AccessRole.ADMIN.value
        and user.is_active
        and (
            ("role" in fields and request.role != AccessRole.ADMIN)
            or ("is_active" in fields and request.is_active is False)
        )
    )

    if removing_active_admin and count_active_admins(db) <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one active admin is required",
        )

    if "role" in fields and request.role is not None:
        user.role = request.role.value

    if "department" in fields:
        user.department = request.department.strip() if request.department else None

    if "is_active" in fields and request.is_active is not None:
        user.is_active = request.is_active

    db.commit()
    db.refresh(user)
    return user


def delete_managed_user(
    db: Session,
    user_id: int,
    current_user: User,
) -> None:
    user = _get_user_or_404(db, user_id)

    if user.email.strip().lower() == settings.PROTECTED_ADMIN_EMAIL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The protected administrator account cannot be deleted",
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account",
        )

    if (
        user.role == AccessRole.ADMIN.value
        and user.is_active
        and count_active_admins(db) <= 1
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one active admin is required",
        )

    try:
        db.delete(user)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This user has related activity and cannot be deleted; deactivate the account instead",
        ) from exc


def _get_user_or_404(db: Session, user_id: int) -> User:
    user = get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user
