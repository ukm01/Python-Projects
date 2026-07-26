from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models.document_model import Document, DocumentStatus
from app.models.user_model import User
from app.repositories.document_access_role_repository import (
    DocumentAccessRoleRepository,
)
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.services.document_access_service import (
    parse_allowed_roles,
    serialize_allowed_roles,
)
from app.services.ingestion.file_storage import StoredFile, save_uploaded_file
from app.services.ingestion.file_validator import validate_upload_metadata
from app.services.ingestion.ingestion_pipeline import ingest_document
from app.services.ingestion.upload_exceptions import (
    DocumentBusyError,
    DuplicateDocumentError,
)
from app.services.ingestion.vector_store import (
    delete_document_vectors,
    delete_vector_ids,
    get_document_vector_ids,
)


@dataclass(frozen=True)
class ReplacementContext:
    previous_values: dict[str, object]
    previous_access_roles: list[str]
    previous_vector_ids: list[str]
    previous_chunk_ids: list[str]
    new_file_path: str


@dataclass(frozen=True)
class QueuedDocument:
    document: Document
    replacement: ReplacementContext | None = None


class DocumentService:

    def __init__(
        self,
        document_repository: DocumentRepository,
        chunk_repository: DocumentChunkRepository | None = None,
        access_role_repository: DocumentAccessRoleRepository | None = None,
    ):
        self.document_repository = document_repository
        self.chunk_repository = (
            chunk_repository
            or DocumentChunkRepository()
        )
        self.access_role_repository = (
            access_role_repository
            or DocumentAccessRoleRepository()
        )

    def list_documents(self, db: Session) -> list[Document]:
        return self.document_repository.list_all(db)

    async def queue_document_upload(
        self,
        db: Session,
        file: UploadFile,
        document_name: str,
        category: str,
        product_name: str | None,
        allowed_roles: str,
        current_user: User,
    ) -> QueuedDocument:
        access_roles = parse_allowed_roles(allowed_roles)
        normalized_allowed_roles = serialize_allowed_roles(access_roles)
        extension = validate_upload_metadata(file)
        stored_file = await save_uploaded_file(
            file=file,
            document_id=uuid4(),
            extension=extension,
        )

        existing_by_name = self.document_repository.get_by_original_filename(
            db=db,
            original_filename=stored_file.original_filename,
        )

        if (
            existing_by_name
            and existing_by_name.status == DocumentStatus.PROCESSING
        ):
            _delete_stored_file(stored_file.storage_path)
            raise DocumentBusyError(
                "A document with this filename is already processing."
            )

        duplicate_document = self.document_repository.get_by_checksum(
            db=db,
            checksum_sha256=stored_file.checksum_sha256,
            exclude_document_id=(
                existing_by_name.id
                if existing_by_name
                else None
            ),
        )

        if duplicate_document:
            _delete_stored_file(stored_file.storage_path)
            raise DuplicateDocumentError(
                "The same document content already exists under another filename."
            )

        if existing_by_name:
            return self._queue_replacement(
                db=db,
                document=existing_by_name,
                stored_file=stored_file,
                document_name=document_name,
                category=category,
                product_name=product_name,
                allowed_roles=normalized_allowed_roles,
                access_roles=access_roles,
                current_user=current_user,
            )

        return self._queue_new_document(
            db=db,
            stored_file=stored_file,
            document_name=document_name,
            category=category,
            product_name=product_name,
            allowed_roles=normalized_allowed_roles,
            access_roles=access_roles,
            current_user=current_user,
        )

    def process_document(
        self,
        document_id: int,
        replacement: ReplacementContext | None,
    ) -> None:
        db = SessionLocal()

        try:
            document = self.document_repository.get_by_id(
                db=db,
                document_id=document_id,
            )

            if (
                not document
                or document.status != DocumentStatus.PROCESSING
            ):
                return

            if replacement:
                self._process_replacement(
                    db=db,
                    document=document,
                    context=replacement,
                )
            else:
                self._process_new_document(
                    db=db,
                    document=document,
                )
        finally:
            db.close()

    def delete_document(
        self,
        db: Session,
        document_id: int,
    ) -> None:
        document = self.document_repository.get_by_id(
            db=db,
            document_id=document_id,
        )

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        if document.status == DocumentStatus.PROCESSING:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A processing document cannot be deleted",
            )

        delete_document_vectors(document.id)
        _delete_stored_file(document.file_path)
        self.document_repository.delete(
            db=db,
            document=document,
        )

    def _queue_new_document(
        self,
        db: Session,
        stored_file: StoredFile,
        document_name: str,
        category: str,
        product_name: str | None,
        allowed_roles: str,
        access_roles: list[str],
        current_user: User,
    ) -> QueuedDocument:
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
            status=DocumentStatus.PROCESSING,
        )

        try:
            saved_document = self.document_repository.create(
                db=db,
                document=document,
            )
            self.access_role_repository.replace_roles(
                db=db,
                document_id=saved_document.id,
                roles=access_roles,
            )
            db.commit()
            db.refresh(saved_document)
            return QueuedDocument(document=saved_document)
        except Exception:
            db.rollback()
            _delete_stored_file(stored_file.storage_path)
            raise

    def _queue_replacement(
        self,
        db: Session,
        document: Document,
        stored_file: StoredFile,
        document_name: str,
        category: str,
        product_name: str | None,
        allowed_roles: str,
        access_roles: list[str],
        current_user: User,
    ) -> QueuedDocument:
        context = ReplacementContext(
            previous_values=_snapshot_document(document),
            previous_access_roles=self.access_role_repository.list_roles(
                db=db,
                document_id=document.id,
            ),
            previous_vector_ids=get_document_vector_ids(document.id),
            previous_chunk_ids=self.chunk_repository.list_chunk_ids(
                db=db,
                document_id=document.id,
            ),
            new_file_path=stored_file.storage_path,
        )

        _apply_replacement_values(
            document=document,
            stored_file=stored_file,
            document_name=document_name,
            category=category,
            product_name=product_name,
            allowed_roles=allowed_roles,
            uploaded_by=current_user.email,
        )
        document.status = DocumentStatus.PROCESSING
        document.error_message = None

        try:
            self.access_role_repository.replace_roles(
                db=db,
                document_id=document.id,
                roles=access_roles,
            )
            db.commit()
            db.refresh(document)
            return QueuedDocument(
                document=document,
                replacement=context,
            )
        except Exception:
            db.rollback()
            _delete_stored_file(stored_file.storage_path)
            raise

    def _process_new_document(
        self,
        db: Session,
        document: Document,
    ) -> None:
        new_vector_ids: list[str] = []

        try:
            new_vector_ids = ingest_document(
                db=db,
                document_record=document,
            )
            document.status = DocumentStatus.READY
            document.error_message = None
            db.commit()
        except Exception as exc:
            db.rollback()

            try:
                delete_vector_ids(new_vector_ids)

                if not new_vector_ids:
                    delete_document_vectors(document.id)
            finally:
                document = self.document_repository.get_by_id(
                    db=db,
                    document_id=document.id,
                )

                if not document:
                    return

                document.status = DocumentStatus.FAILED
                document.error_message = str(exc)
                db.commit()

    def _process_replacement(
        self,
        db: Session,
        document: Document,
        context: ReplacementContext,
    ) -> None:
        new_vector_ids: list[str] = []

        try:
            new_vector_ids = ingest_document(
                db=db,
                document_record=document,
            )

            self.chunk_repository.delete_chunk_ids(
                db=db,
                chunk_ids=context.previous_chunk_ids,
            )
            document.status = DocumentStatus.READY
            document.error_message = None
            db.commit()
        except Exception as exc:
            self._rollback_replacement(
                db=db,
                document_id=document.id,
                context=context,
                error=exc,
                new_vector_ids=new_vector_ids,
            )
            return

        try:
            delete_vector_ids(context.previous_vector_ids)
        except Exception:
            # PostgreSQL already points to the new active chunk set. Old
            # Chroma entries are harmless orphans and can be cleaned later.
            pass

        try:
            _delete_stored_file(
                str(context.previous_values["file_path"])
            )
        except OSError:
            # The replacement is committed and searchable. Leaving an old
            # orphan file is safer than reverting valid new vector data.
            pass

    def _rollback_replacement(
        self,
        db: Session,
        document_id: int,
        context: ReplacementContext,
        error: Exception,
        new_vector_ids: list[str],
    ) -> None:
        db.rollback()

        try:
            delete_vector_ids(new_vector_ids)
        finally:
            document = self.document_repository.get_by_id(
                db=db,
                document_id=document_id,
            )

            if not document:
                return

            _restore_document(document, context.previous_values)
            self.access_role_repository.replace_roles(
                db=db,
                document_id=document.id,
                roles=context.previous_access_roles,
            )
            document.error_message = (
                f"Replacement failed; previous version restored: {error}"
            )
            db.commit()

            try:
                _delete_stored_file(context.new_file_path)
            except OSError:
                pass


def _snapshot_document(document: Document) -> dict[str, object]:
    return {
        "document_name": document.document_name,
        "original_filename": document.original_filename,
        "stored_filename": document.stored_filename,
        "file_path": document.file_path,
        "file_extension": document.file_extension,
        "mime_type": document.mime_type,
        "size_bytes": document.size_bytes,
        "checksum_sha256": document.checksum_sha256,
        "category": document.category,
        "product_name": document.product_name,
        "allowed_roles": document.allowed_roles,
        "uploaded_by": document.uploaded_by,
        "status": document.status,
        "error_message": document.error_message,
    }


def _restore_document(
    document: Document,
    values: dict[str, object],
) -> None:
    for field, value in values.items():
        setattr(document, field, value)


def _apply_replacement_values(
    document: Document,
    stored_file: StoredFile,
    document_name: str,
    category: str,
    product_name: str | None,
    allowed_roles: str,
    uploaded_by: str,
) -> None:
    document.document_name = document_name
    document.original_filename = stored_file.original_filename
    document.stored_filename = stored_file.stored_filename
    document.file_path = stored_file.storage_path
    document.file_extension = stored_file.extension
    document.mime_type = stored_file.detected_mime_type
    document.size_bytes = stored_file.size_bytes
    document.checksum_sha256 = stored_file.checksum_sha256
    document.category = category
    document.product_name = product_name
    document.allowed_roles = allowed_roles
    document.uploaded_by = uploaded_by


def _delete_stored_file(file_path: str) -> None:
    target_path = Path(file_path).resolve()
    raw_docs_directory = Path(settings.RAW_DOCS_DIR).resolve()

    if not target_path.is_relative_to(raw_docs_directory):
        raise RuntimeError(
            "Refusing to delete a document outside the configured upload directory"
        )

    target_path.unlink(missing_ok=True)
