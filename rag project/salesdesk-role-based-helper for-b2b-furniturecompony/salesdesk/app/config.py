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
    PROTECTED_ADMIN_EMAIL: str = os.getenv(
        "PROTECTED_ADMIN_EMAIL",
        "admin@9to5.com",
    ).strip().lower()
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
    )
    PASSWORD_RESET_OTP_EXPIRE_MINUTES: int = int(
        os.getenv("PASSWORD_RESET_OTP_EXPIRE_MINUTES", "10")
    )
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("PASSWORD_RESET_TOKEN_EXPIRE_MINUTES", "10")
    )
    PASSWORD_RESET_MAX_ATTEMPTS: int = int(
        os.getenv("PASSWORD_RESET_MAX_ATTEMPTS", "5")
    )

    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL: str = os.getenv("SMTP_FROM_EMAIL", "")
    SMTP_USE_TLS: bool = (
        os.getenv("SMTP_USE_TLS", "true").strip().lower()
        in {"1", "true", "yes", "on"}
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

    RERANKER_MODEL_NAME: str = os.getenv(
        "RERANKER_MODEL_NAME",
        "BAAI/bge-reranker-base",
    )
    RERANKER_DEVICE: str = os.getenv(
        "RERANKER_DEVICE",
        "cpu",
    )
    RERANKER_BATCH_SIZE: int = int(
        os.getenv("RERANKER_BATCH_SIZE", "8")
    )
    RERANKER_MAX_LENGTH: int = int(
        os.getenv("RERANKER_MAX_LENGTH", "512")
    )

    LLM_BASE_URL: str = os.getenv(
        "LLM_BASE_URL",
        "https://api.groq.com/openai/v1",
    )
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv(
        "LLM_MODEL",
        "openai/gpt-oss-20b",
    )
    LLM_TEMPERATURE: float = float(
        os.getenv("LLM_TEMPERATURE", "0.1")
    )
    LLM_MAX_OUTPUT_TOKENS: int = int(
        os.getenv("LLM_MAX_OUTPUT_TOKENS", "800")
    )
    LLM_CONTEXT_TOP_K: int = int(
        os.getenv("LLM_CONTEXT_TOP_K", "5")
    )
    RERANKER_MIN_SCORE: float = float(
        os.getenv("RERANKER_MIN_SCORE", "0.10")
    )
    LLM_TIMEOUT_SECONDS: float = float(
        os.getenv("LLM_TIMEOUT_SECONDS", "45")
    )

    MAX_UPLOAD_SIZE_MB: int = int(
        os.getenv("MAX_UPLOAD_SIZE_MB", "25")
    )

    MAX_UPLOAD_SIZE_BYTES: int = (
        MAX_UPLOAD_SIZE_MB * 1024 * 1024
    )


settings = Settings()
