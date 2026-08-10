from dataclasses import dataclass

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models.document_access_role_model import DocumentAccessRole
from app.models.document_chunk_model import DocumentChunk
from app.models.document_model import Document, DocumentStatus


@dataclass(frozen=True)
class AuthorizedChunk:
    chunk_id: str
    document_id: int
    content: str
    page_number: int | None
    chunk_index: int
    document_name: str
    original_filename: str
    category: str


class RetrievalRepository:

    def get_authorized_chunks(
        self,
        db: Session,
        role: str,
        chunk_ids: list[str],
    ) -> dict[str, AuthorizedChunk]:
        if not chunk_ids:
            return {}

        rows = (
            db.query(DocumentChunk, Document)
            .join(
                Document,
                Document.id == DocumentChunk.document_id,
            )
            .join(
                DocumentAccessRole,
                and_(
                    DocumentAccessRole.document_id == Document.id,
                    DocumentAccessRole.role == role,
                ),
            )
            .filter(
                DocumentChunk.chunk_id.in_(chunk_ids),
                Document.status == DocumentStatus.READY,
            )
            .all()
        )

        return {
            chunk.chunk_id: _to_authorized_chunk(chunk, document)
            for chunk, document in rows
        }

    def keyword_search(
        self,
        db: Session,
        role: str,
        question: str,
        limit: int,
    ) -> list[tuple[AuthorizedChunk, float]]:
        search_query = func.plainto_tsquery("english", question)
        rank = func.ts_rank_cd(
            DocumentChunk.search_vector,
            search_query,
        )

        rows = (
            db.query(DocumentChunk, Document, rank.label("rank"))
            .join(
                Document,
                Document.id == DocumentChunk.document_id,
            )
            .join(
                DocumentAccessRole,
                and_(
                    DocumentAccessRole.document_id == Document.id,
                    DocumentAccessRole.role == role,
                ),
            )
            .filter(
                Document.status == DocumentStatus.READY,
                DocumentChunk.search_vector.op("@@")(search_query),
            )
            .order_by(rank.desc(), DocumentChunk.id)
            .limit(limit)
            .all()
        )

        return [
            (
                _to_authorized_chunk(chunk, document),
                float(keyword_rank),
            )
            for chunk, document, keyword_rank in rows
        ]


def _to_authorized_chunk(
    chunk: DocumentChunk,
    document: Document,
) -> AuthorizedChunk:
    return AuthorizedChunk(
        chunk_id=chunk.chunk_id,
        document_id=document.id,
        content=chunk.content,
        page_number=chunk.page_number,
        chunk_index=chunk.chunk_index,
        document_name=document.document_name,
        original_filename=document.original_filename,
        category=document.category,
    )
