from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.repositories.query_log_repository import QueryLogRepository
from app.services.llm_service import LlmService
from app.services.retrieval_service import RetrievalService


NO_CONTEXT_ANSWER = (
    "I could not find enough relevant information in the policy "
    "documents you can access."
)


class ChatService:

    def __init__(
        self,
        retrieval_service: RetrievalService | None = None,
        llm_service: LlmService | None = None,
        query_log_repository: QueryLogRepository | None = None,
    ):
        self.retrieval_service = (
            retrieval_service
            or RetrievalService()
        )
        self.llm_service = llm_service or LlmService()
        self.query_log_repository = (
            query_log_repository
            or QueryLogRepository()
        )

    def ask(
        self,
        db: Session,
        user_id: int,
        role: str,
        question: str,
    ) -> dict:
        retrieved_chunks = self.retrieval_service.search(
            db=db,
            question=question,
            role=role,
            top_k=settings.LLM_CONTEXT_TOP_K,
        )
        relevant_chunks = [
            chunk
            for chunk in retrieved_chunks
            if (
                chunk.get("reranker_score") is not None
                and chunk["reranker_score"]
                >= settings.RERANKER_MIN_SCORE
            )
        ]
        sources = [
            {
                **chunk,
                "source_id": f"S{index}",
            }
            for index, chunk in enumerate(
                relevant_chunks,
                start=1,
            )
        ]

        if not sources:
            response = {
                "status": "insufficient_context",
                "answer": NO_CONTEXT_ANSWER,
                "citations": [],
                "model": settings.LLM_MODEL,
            }
            self._save_query_log(
                db=db,
                user_id=user_id,
                question=question,
                response=response,
            )
            return response

        llm_answer = self.llm_service.generate_answer(
            question=question,
            sources=sources,
        )
        sources_by_id = {
            source["source_id"]: source
            for source in sources
        }
        citation_ids = list(
            dict.fromkeys(
                citation.source_id
                for citation in llm_answer.citations
            )
        )
        if any(
            source_id not in sources_by_id
            for source_id in citation_ids
        ):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="The language model cited an unknown source.",
            )
        citations = [
            _serialize_citation(
                sources_by_id[source_id]
            )
            for source_id in citation_ids
        ]
        response = {
            "status": llm_answer.status,
            "answer": llm_answer.answer,
            "citations": citations,
            "model": settings.LLM_MODEL,
        }
        self._save_query_log(
            db=db,
            user_id=user_id,
            question=question,
            response=response,
        )
        return response

    def _save_query_log(
        self,
        db: Session,
        user_id: int,
        question: str,
        response: dict,
    ) -> None:
        try:
            self.query_log_repository.create(
                db=db,
                user_id=user_id,
                question=question,
                answer=response["answer"],
                sources=response["citations"],
            )
        except Exception:
            db.rollback()


def _serialize_citation(source: dict) -> dict:
    return {
        "source_id": source["source_id"],
        "chunk_id": source["chunk_id"],
        "document_id": source["document_id"],
        "document_name": source["document_name"],
        "original_filename": source["original_filename"],
        "page_number": source["page_number"],
    }
