from pathlib import Path

from fastapi import UploadFile

from app.services.ingestion.file_types import (
    ALLOWED_EXTENSIONS,
    EXTENSION_TO_MIME_TYPES,
)
from app.services.ingestion.upload_exceptions import (
    FileTypeMismatchError,
    MissingFilenameError,
    UnsupportedFileTypeError,
)


def validate_upload_metadata(file: UploadFile) -> str:
    if not file.filename:
        raise MissingFilenameError(
            "The uploaded file has no filename."
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise UnsupportedFileTypeError(
            f"File type '{extension}' is not supported."
        )

    declared_mime_type = (file.content_type or "").lower()

    expected_mime_types = EXTENSION_TO_MIME_TYPES[extension]

    if declared_mime_type not in expected_mime_types:
        raise FileTypeMismatchError(
            f"File extension '{extension}' does not match "
            f"MIME type '{declared_mime_type}'."
        )

    return extension