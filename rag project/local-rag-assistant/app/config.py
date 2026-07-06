from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    UPLOAD_DIR: str = "uploaded_files"
    CHROMA_PERSIST_DIR: str = "chroma_storage"
    CHROMA_COLLECTION_NAME: str = "documents"
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 150

    class Config:
        env_file = ".env"


settings = Settings()