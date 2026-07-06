from app.services.embedding_service import embedding_service
from app.services.vector_store_service import vector_store_service


class RetrievalService:
    def retrieve_relevant_chunks(
        self,
        question: str,
        top_k: int = 3
    ) -> list[dict]:
        query_embedding = embedding_service.embed_query(question)

        retrieved_chunks = vector_store_service.search_similar_chunks(
            query_embedding=query_embedding,
            top_k=top_k
        )

        return retrieved_chunks


retrieval_service = RetrievalService()