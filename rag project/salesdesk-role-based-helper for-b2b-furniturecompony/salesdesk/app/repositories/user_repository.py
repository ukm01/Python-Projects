from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.user_model import User


def get_user_by_email(db: Session, email: str) -> User | None:
    normalized_email = email.strip().lower()

    return (
        db.query(User)
        .filter(func.lower(User.email) == normalized_email)
        .first()
    )


def create_user(
    db: Session,
    name: str,
    email: str,
    hashed_password: str,
    role: str,
    department: str | None = None,
    is_active: bool = True
) -> User:
    user = User(
        name=name.strip(),
        email=email.strip().lower(),
        hashed_password=hashed_password,
        role=role,
        department=department,
        is_active=is_active
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def list_users(db: Session) -> list[User]:
    return db.query(User).order_by(User.created_at.desc(), User.id.desc()).all()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def count_active_admins(db: Session) -> int:
    return (
        db.query(User)
        .filter(User.role == "admin", User.is_active.is_(True))
        .count()
    )
