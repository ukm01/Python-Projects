from sqlalchemy.orm import Session

from app.models.document_chunk_model import DocumentChunk


class DocumentChunkRepository:

    def list_chunk_ids(
        self,
        db: Session,
        document_id: int,
    ) -> list[str]:
        rows = (
            db.query(DocumentChunk.chunk_id)
            .filter(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index)
            .all()
        )
        return [row[0] for row in rows]

    def delete_chunk_ids(
        self,
        db: Session,
        chunk_ids: list[str],
    ) -> None:
        if not chunk_ids:
            return

        (
            db.query(DocumentChunk)
            .filter(DocumentChunk.chunk_id.in_(chunk_ids))
            .delete(synchronize_session=False)
        )

    def count_for_document(
        self,
        db: Session,
        document_id: int,
    ) -> int:
        return (
            db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document_id)
            .count()
        )
