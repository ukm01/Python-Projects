from langchain_chroma import Chroma

from app.config import settings
from app.services.ingestion.embedding_model import embedding_model


vector_store = Chroma(
    collection_name="salesdesk_documents",
    embedding_function=embedding_model,
    persist_directory=settings.VECTOR_DB_DIR,
)