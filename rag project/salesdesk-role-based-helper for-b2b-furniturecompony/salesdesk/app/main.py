from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.health_routes import router as health_router
from app.api.auth_routes import router as auth_router
from app.api.document_routes import router as document_router
from app.database import Base, engine

from app.models.user_model import User
from app.models.document_model import Document
from app.models.query_log_model import QueryLog


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SalesDesk RAG API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    errors = []

    for error in exc.errors():
        field_path = [
            str(location)
            for location in error["loc"]
            if location != "body"
        ]

        errors.append({
            "field": ".".join(field_path),
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "message": "Request validation failed",
            "errors": errors
        }
    )


app.include_router(health_router)
app.include_router(auth_router)
app.include_router(document_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to SalesDesk RAG API"
    }
