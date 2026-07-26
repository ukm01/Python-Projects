from sqlalchemy.orm import Session

from app.models.document_model import Document, DocumentStatus


class DocumentRepository:

    def get_by_checksum(
        self,
        db: Session,
        checksum_sha256: str,
    ) -> Document | None:

        return (
            db.query(Document)
            .filter(
                Document.checksum_sha256 == checksum_sha256,
                Document.status != DocumentStatus.ARCHIVED,
            )
            .first()
        )

    def create(
        self,
        db: Session,
        document: Document,
    ) -> Document:

        db.add(document)
        db.commit()
        db.refresh(document)

        return document