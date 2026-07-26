
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.document_model import Document, DocumentStatus
from app.models.user_model import User
from app.repositories.document_repository import DocumentRepository
from app.services.ingestion.file_storage import save_uploaded_file
from app.services.ingestion.file_validator import validate_upload_metadata
from app.services.ingestion.ingestion_pipeline import ingest_document
from app.services.ingestion.upload_exceptions import DuplicateDocumentError


class DocumentService:

    def __init__(
        self,
        document_repository: DocumentRepository,
    ):
        self.document_repository = document_repository

    async def upload_document(
        self,
        db: Session,
        file: UploadFile,
        document_name: str,
        category: str,
        product_name: str | None,
        allowed_roles: str,
        current_user: User,
    ) -> Document:

        extension = validate_upload_metadata(file)

        storage_id = uuid4()

        stored_file = await save_uploaded_file(
            file=file,
            document_id=storage_id,
            extension=extension,
        )

        existing_document = (
            self.document_repository.get_by_checksum(
                db=db,
                checksum_sha256=stored_file.checksum_sha256,
            )
        )

        if existing_document:
            Path(
                stored_file.storage_path
            ).unlink(missing_ok=True)

            raise DuplicateDocumentError(
                "The same document has already been uploaded."
            )

        document = Document(
            document_name=document_name,
            original_filename=stored_file.original_filename,
            stored_filename=stored_file.stored_filename,
            file_path=stored_file.storage_path,
            file_extension=stored_file.extension,
            mime_type=stored_file.detected_mime_type,
            size_bytes=stored_file.size_bytes,
            checksum_sha256=stored_file.checksum_sha256,
            category=category,
            product_name=product_name,
            allowed_roles=allowed_roles,
            uploaded_by=current_user.email,
            status=DocumentStatus.UPLOADED,
        )

        try:
            saved_document = self.document_repository.create(
                db=db,
                document=document,
            )

            saved_document.status = DocumentStatus.PROCESSING

            db.commit()
            db.refresh(saved_document)

            try:
                ingest_document(saved_document)

                saved_document.status = DocumentStatus.READY
                saved_document.error_message = None

            except Exception as exc:
                saved_document.status = DocumentStatus.FAILED
                saved_document.error_message = str(exc)

                db.commit()
                db.refresh(saved_document)

                raise

            db.commit()
            db.refresh(saved_document)

            return saved_document

        except Exception:
            db.rollback()

            if document.id is None:
                Path(
                    stored_file.storage_path
                ).unlink(missing_ok=True)

            raise

