from app.config import settings
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

    def filter_chunks_by_distance(
        self,
        retrieved_chunks: list[dict]
    ) -> list[dict]:
        filtered_chunks = []

        for chunk in retrieved_chunks:
            if chunk["distance"] <= settings.MAX_RETRIEVAL_DISTANCE:
                filtered_chunks.append(chunk)

        return filtered_chunks

    def is_retrieval_confident(
        self,
        retrieved_chunks: list[dict]
    ) -> bool:
        if not retrieved_chunks:
            return False

        best_distance = retrieved_chunks[0]["distance"]

        return best_distance <= settings.MAX_RETRIEVAL_DISTANCE


retrieval_service = RetrievalService()