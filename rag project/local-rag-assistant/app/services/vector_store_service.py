import chromadb
from app.config import settings


class VectorStoreService:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR
        )

        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"description": "Document chunks for local RAG"}
        )

    def add_chunks(
        self,
        document_id: str,
        file_name: str,
        chunks: list[dict],
        embeddings: list[list[float]]
    ) -> int:
        ids = []
        documents = []
        metadatas = []

        for chunk, embedding in zip(chunks, embeddings):
            chunk_id = f"{document_id}_chunk_{chunk['chunk_index']}"

            ids.append(chunk_id)
            documents.append(chunk["text"])
            metadatas.append(
                {
                    "document_id": document_id,
                    "file_name": file_name,
                    "page_number": chunk["page_number"],
                    "chunk_index": chunk["chunk_index"]
                }
            )

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

        return len(ids)


vector_store_service = VectorStoreService()