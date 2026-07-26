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