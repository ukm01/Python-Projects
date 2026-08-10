from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.sql import func

from app.database import Base


class DocumentAccessRole(Base):
    __tablename__ = "document_access_roles"

    document_id = Column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role = Column(
        String(50),
        primary_key=True,
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        CheckConstraint(
            "role IN ('admin', 'sales', 'manager')",
            name="ck_document_access_roles_valid_role",
        ),
        Index("ix_document_access_roles_role", "role"),
    )
