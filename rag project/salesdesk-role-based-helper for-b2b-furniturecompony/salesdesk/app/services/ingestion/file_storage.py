import hashlib
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

import aiofiles
import filetype
from fastapi import UploadFile

from app.config import settings
from app.services.ingestion.file_types import EXTENSION_TO_MIME_TYPES
from app.services.ingestion.upload_exceptions import (
    EmptyFileError,
    FileTooLargeError,
    FileTypeMismatchError,
)


READ_BUFFER_SIZE = 1024 * 1024  # 1 MB


@dataclass(frozen=True)
class StoredFile:
    storage_path: str
    stored_filename: str
    original_filename: str
    extension: str
    detected_mime_type: str
    size_bytes: int
    checksum_sha256: str


async def save_uploaded_file(
    file: UploadFile,
    document_id: UUID,
    extension: str,
) -> StoredFile:

    upload_directory = Path(settings.RAW_DOCS_DIR)

    upload_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    stored_filename = f"{document_id}{extension}"

    destination_path = (
        upload_directory / stored_filename
    )

    sha256_hash = hashlib.sha256()

    total_size = 0

    signature_buffer = bytearray()

    try:
        async with aiofiles.open(
            destination_path,
            "wb",
        ) as output_file:

            while chunk := await file.read(
                READ_BUFFER_SIZE
            ):
                total_size += len(chunk)

                if (
                    total_size
                    > settings.MAX_UPLOAD_SIZE_BYTES
                ):
                    raise FileTooLargeError(
                        "Uploaded file exceeds "
                        f"{settings.MAX_UPLOAD_SIZE_MB} MB."
                    )

                if len(signature_buffer) < 8192:
                    remaining = (
                        8192 - len(signature_buffer)
                    )

                    signature_buffer.extend(
                        chunk[:remaining]
                    )

                sha256_hash.update(chunk)

                await output_file.write(chunk)

        if total_size == 0:
            raise EmptyFileError(
                "Uploaded file is empty."
            )

        detected_mime_type = (
            validate_file_signature(
                file_header=bytes(signature_buffer),
                extension=extension,
                declared_mime_type=file.content_type,
            )
        )

        return StoredFile(
            storage_path=str(destination_path.resolve()),
            stored_filename=stored_filename,
            original_filename=(
                file.filename or stored_filename
            ),
            extension=extension,
            detected_mime_type=detected_mime_type,
            size_bytes=total_size,
            checksum_sha256=sha256_hash.hexdigest(),
        )

    except Exception:
        destination_path.unlink(
            missing_ok=True
        )
        raise

    finally:
        await file.close()


def validate_file_signature(
    file_header: bytes,
    extension: str,
    declared_mime_type: str | None,
) -> str:

    detected_kind = filetype.guess(file_header)

    text_extensions = {
        ".txt",
        ".csv",
        ".html",
        ".htm",
    }

    if detected_kind is None:
        if extension in text_extensions:
            return (
                declared_mime_type
                or "text/plain"
            )

        raise FileTypeMismatchError(
            "Actual file type could not be verified."
        )

    detected_mime_type = (
        detected_kind.mime.lower()
    )

    expected_mime_types = (
        EXTENSION_TO_MIME_TYPES[extension]
    )

    if (
        detected_mime_type
        not in expected_mime_types
    ):
        raise FileTypeMismatchError(
            f"Actual file type "
            f"'{detected_mime_type}' "
            f"does not match extension "
            f"'{extension}'."
        )

    return detected_mime_type