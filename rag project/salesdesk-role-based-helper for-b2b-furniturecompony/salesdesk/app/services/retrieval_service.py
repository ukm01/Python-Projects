from dataclasses import dataclass, field

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.document_access_role_repository import (
    DocumentAccessRoleRepository,
)
from app.repositories.retrieval_repository import (
    AuthorizedChunk,
    RetrievalRepository,
)
from app.security.roles import ACCESS_ROLES
from app.services.ingestion.vector_store import vector_store
from app.services.reranker import score_passages


VECTOR_CANDIDATE_LIMIT = 20
KEYWORD_CANDIDATE_LIMIT = 20
RRF_CONSTANT = 60


@dataclass
class _MergedCandidate:
    chunk: AuthorizedChunk
    hybrid_score: float = 0.0
    reranker_score: float | None = None
    reranker_rank: int | None = None
    vector_rank: int | None = None
    keyword_rank: int | None = None
    vector_distance: float | None = None
    keyword_score: float | None = None
    match_types: set[str] = field(default_factory=set)


class RetrievalService:

    def __init__(
        self,
        access_repository: DocumentAccessRoleRepository | None = None,
        retrieval_repository: RetrievalRepository | None = None,
    ):
        self.access_repository = (
            access_repository
            or DocumentAccessRoleRepository()
        )
        self.retrieval_repository = (
            retrieval_repository
            or RetrievalRepository()
        )

    def search(
        self,
        db: Session,
        question: str,
        role: str,
        top_k: int,
    ) -> list[dict]:
        normalized_role = role.strip().lower()
        if normalized_role not in ACCESS_ROLES:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account role cannot access documents.",
            )

        accessible_document_ids = (
            self.access_repository.list_accessible_document_ids(
                db=db,
                role=normalized_role,
            )
        )
        if not accessible_document_ids:
            return []

        vector_hits = self._vector_search(
            question=question,
            document_ids=accessible_document_ids,
        )
        authorized_vector_chunks = (
            self.retrieval_repository.get_authorized_chunks(
                db=db,
                role=normalized_role,
                chunk_ids=[chunk_id for chunk_id, _ in vector_hits],
            )
        )
        keyword_hits = self.retrieval_repository.keyword_search(
            db=db,
            role=normalized_role,
            question=question,
            limit=KEYWORD_CANDIDATE_LIMIT,
        )

        merged: dict[str, _MergedCandidate] = {}
        for rank, (chunk_id, distance) in enumerate(
            vector_hits,
            start=1,
        ):
            chunk = authorized_vector_chunks.get(chunk_id)
            if not chunk:
                continue

            candidate = merged.setdefault(
                chunk_id,
                _MergedCandidate(chunk=chunk),
            )
            candidate.hybrid_score += 1 / (RRF_CONSTANT + rank)
            candidate.vector_rank = rank
            candidate.vector_distance = distance
            candidate.match_types.add("vector")

        for rank, (chunk, keyword_score) in enumerate(
            keyword_hits,
            start=1,
        ):
            candidate = merged.setdefault(
                chunk.chunk_id,
                _MergedCandidate(chunk=chunk),
            )
            candidate.hybrid_score += 1 / (RRF_CONSTANT + rank)
            candidate.keyword_rank = rank
            candidate.keyword_score = keyword_score
            candidate.match_types.add("keyword")

        ranked = sorted(
            merged.values(),
            key=lambda candidate: (
                -candidate.hybrid_score,
                candidate.chunk.document_id,
                candidate.chunk.chunk_index,
            ),
        )
        reranker_scores = score_passages(
            question=question,
            passages=[
                candidate.chunk.content
                for candidate in ranked
            ],
        )
        for candidate, reranker_score in zip(
            ranked,
            reranker_scores,
            strict=True,
        ):
            candidate.reranker_score = reranker_score

        reranked = sorted(
            ranked,
            key=lambda candidate: (
                -(
                    candidate.reranker_score
                    if candidate.reranker_score is not None
                    else float("-inf")
                ),
                -candidate.hybrid_score,
            ),
        )
        for reranker_rank, candidate in enumerate(
            reranked,
            start=1,
        ):
            candidate.reranker_rank = reranker_rank

        return [
            _serialize_candidate(candidate)
            for candidate in reranked[:top_k]
        ]

    def _vector_search(
        self,
        question: str,
        document_ids: list[int],
    ) -> list[tuple[str, float]]:
        document_filter: dict = {
            "document_id": (
                document_ids[0]
                if len(document_ids) == 1
                else {"$in": document_ids}
            )
        }
        results = vector_store.similarity_search_with_score(
            query=question,
            k=VECTOR_CANDIDATE_LIMIT,
            filter=document_filter,
        )

        hits: list[tuple[str, float]] = []
        for document, distance in results:
            chunk_id = document.metadata.get("chunk_id")
            if isinstance(chunk_id, str):
                hits.append((chunk_id, float(distance)))
        return hits


def _serialize_candidate(candidate: _MergedCandidate) -> dict:
    chunk = candidate.chunk
    return {
        "chunk_id": chunk.chunk_id,
        "document_id": chunk.document_id,
        "document_name": chunk.document_name,
        "original_filename": chunk.original_filename,
        "category": chunk.category,
        "page_number": chunk.page_number,
        "chunk_index": chunk.chunk_index,
        "content": chunk.content,
        "score": candidate.reranker_score,
        "hybrid_score": candidate.hybrid_score,
        "reranker_score": candidate.reranker_score,
        "reranker_rank": candidate.reranker_rank,
        "match_types": sorted(candidate.match_types),
        "vector_rank": candidate.vector_rank,
        "keyword_rank": candidate.keyword_rank,
        "vector_distance": candidate.vector_distance,
        "keyword_score": candidate.keyword_score,
    }
