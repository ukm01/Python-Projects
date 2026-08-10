from fastapi import FastAPI
from app.api.document_routes import router as document_router
from app.api.query_routes import router as query_router

app = FastAPI(
    title="Local RAG Assistant",
    description="A local RAG application using FastAPI, ChromaDB, and sentence-transformers",
    version="1.0.0"
)

app.include_router(document_router)
app.include_router(query_router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "Local RAG Assistant is running"
    }
