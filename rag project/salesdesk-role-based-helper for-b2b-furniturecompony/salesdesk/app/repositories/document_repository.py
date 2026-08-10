from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.document_model import Document, DocumentStatus


class DocumentRepository:

    def get_by_checksum(
        self,
        db: Session,
        checksum_sha256: str,
        exclude_document_id: int | None = None,
    ) -> Document | None:
        query = (
            db.query(Document)
            .filter(
                Document.checksum_sha256 == checksum_sha256,
                Document.status != DocumentStatus.ARCHIVED,
            )
        )

        if exclude_document_id is not None:
            query = query.filter(Document.id != exclude_document_id)

        return query.first()

    def get_by_original_filename(
        self,
        db: Session,
        original_filename: str,
    ) -> Document | None:
        return (
            db.query(Document)
            .filter(
                func.lower(Document.original_filename)
                == original_filename.strip().lower(),
                Document.status != DocumentStatus.ARCHIVED,
            )
            .first()
        )

    def get_by_id(
        self,
        db: Session,
        document_id: int,
    ) -> Document | None:
        return (
            db.query(Document)
            .filter(
                Document.id == document_id,
                Document.status != DocumentStatus.ARCHIVED,
            )
            .first()
        )

    def list_all(self, db: Session) -> list[Document]:
        return (
            db.query(Document)
            .filter(Document.status != DocumentStatus.ARCHIVED)
            .order_by(Document.updated_at.desc(), Document.id.desc())
            .all()
        )

    def create(
        self,
        db: Session,
        document: Document,
    ) -> Document:

        db.add(document)
        db.flush()
        db.refresh(document)

        return document

    def delete(
        self,
        db: Session,
        document: Document,
    ) -> None:
        db.delete(document)
        db.commit()
