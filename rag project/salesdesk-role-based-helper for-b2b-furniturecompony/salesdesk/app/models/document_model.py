import enum

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Enum,
    Integer,
    String,
    Text,
)
from sqlalchemy.sql import func

from app.database import Base


class DocumentStatus(str, enum.Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"


class Document(Base):
    __tablename__ = "documents"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    document_name = Column(
        String,
        nullable=False,
    )

    original_filename = Column(
        String,
        nullable=False,
    )

    stored_filename = Column(
        String,
        nullable=False,
        unique=True,
    )

    file_path = Column(
        String,
        nullable=False,
    )

    file_extension = Column(
        String(20),
        nullable=False,
    )

    mime_type = Column(
        String(150),
        nullable=False,
    )

    size_bytes = Column(
        BigInteger,
        nullable=False,
    )

    checksum_sha256 = Column(
        String(64),
        nullable=False,
        index=True,
    )

    category = Column(
        String,
        nullable=False,
    )

    product_name = Column(
        String,
        nullable=True,
    )

    allowed_roles = Column(
        Text,
        nullable=False,
    )

    uploaded_by = Column(
        String,
        nullable=False,
    )

    status = Column(
        Enum(
            DocumentStatus,
            name="document_status",
        ),
        default=DocumentStatus.UPLOADED,
        nullable=False,
    )

    error_message = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )