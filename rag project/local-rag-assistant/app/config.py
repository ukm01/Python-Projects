from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    UPLOAD_DIR: str = "uploaded_files"
    CHROMA_PERSIST_DIR: str = "chroma_storage"
    CHROMA_COLLECTION_NAME: str = "documents"
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 150
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:3b"
    MAX_RETRIEVAL_DISTANCE: float = 1.2

    class Config:
        env_file = ".env"


settings = Settings()