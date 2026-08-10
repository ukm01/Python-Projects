from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.document_model import DocumentStatus


class DocumentUploadResponse(BaseModel):
    id: int
    document_name: str
    original_filename: str
    mime_type: str
    size_bytes: int
    status: DocumentStatus
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class DocumentListItemResponse(BaseModel):
    id: int
    document_name: str
    original_filename: str
    mime_type: str
    size_bytes: int
    category: str
    product_name: str | None
    allowed_roles: str
    uploaded_by: str
    status: DocumentStatus
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
