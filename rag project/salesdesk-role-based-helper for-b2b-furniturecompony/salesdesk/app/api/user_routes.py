from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user_model import User
from app.schemas.user_schema import (
    UserCreateRequest,
    UserResponse,
    UserUpdateRequest,
)
from app.security.dependencies import require_admin
from app.services.user_service import (
    create_managed_user,
    delete_managed_user,
    get_users,
    update_managed_user,
)


router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(require_admin)],
)


@router.get("", response_model=list[UserResponse])
def list_all_users(db: Session = Depends(get_db)):
    return get_users(db)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    request: UserCreateRequest,
    db: Session = Depends(get_db),
):
    return create_managed_user(db=db, request=request)


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    request: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return update_managed_user(
        db=db,
        user_id=user_id,
        request=request,
        current_user=current_user,
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    delete_managed_user(
        db=db,
        user_id=user_id,
        current_user=current_user,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
