from langchain_chroma import Chroma

from app.config import settings
from app.services.ingestion.embedding_model import embedding_model


vector_store = Chroma(
    collection_name="salesdesk_documents",
    embedding_function=embedding_model,
    persist_directory=settings.VECTOR_DB_DIR,
)


def get_document_vector_ids(document_id: int) -> list[str]:
    result = vector_store.get(
        where={"document_id": document_id},
        include=[],
    )
    return list(result.get("ids") or [])


def delete_vector_ids(vector_ids: list[str]) -> None:
    if vector_ids:
        vector_store.delete(ids=vector_ids)


def delete_document_vectors(document_id: int) -> None:
    delete_vector_ids(
        get_document_vector_ids(document_id)
    )
