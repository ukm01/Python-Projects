from sqlalchemy.orm import Session

from app.models.user_model import User


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


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
        name=name,
        email=email,
        hashed_password=hashed_password,
        role=role,
        department=department,
        is_active=is_active
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user