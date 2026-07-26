import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "SalesDesk RAG API")

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/salesdesk_rag_db"
    )

    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY",
        "change-this-secret-key"
    )
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
    )

    RAW_DOCS_DIR: str = os.getenv(
        "RAW_DOCS_DIR",
        "data/raw_docs"
    )

    UPLOADED_EXCELS_DIR: str = os.getenv(
        "UPLOADED_EXCELS_DIR",
        "data/uploaded_excels"
    )

    VECTOR_DB_DIR: str = os.getenv(
        "VECTOR_DB_DIR",
        "vector_db"
    )

    MAX_UPLOAD_SIZE_MB: int = int(
        os.getenv("MAX_UPLOAD_SIZE_MB", "25")
    )

    MAX_UPLOAD_SIZE_BYTES: int = (
        MAX_UPLOAD_SIZE_MB * 1024 * 1024
    )


settings = Settings()