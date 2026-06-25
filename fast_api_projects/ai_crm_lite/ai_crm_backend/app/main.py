from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db

app = FastAPI(
    title="AI CRM Lite API",
    description="FastAPI + PostgreSQL + AI CRM Backend",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "AI CRM Lite API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AI CRM Lite Backend"
    }


@app.get("/db-test")
def db_test(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1"))
    return {
        "database": "connected",
        "result": result.scalar()
    }