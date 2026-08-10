from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user_model import User
from app.schemas.retrieval_schema import RetrievalRequest, RetrievalResponse
from app.security.dependencies import get_current_user
from app.services.retrieval_service import RetrievalService


router = APIRouter(
    prefix="/retrieval",
    tags=["Retrieval"],
)

retrieval_service = RetrievalService()


@router.post(
    "/search",
    response_model=RetrievalResponse,
)
def search_documents(
    request: RetrievalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    results = retrieval_service.search(
        db=db,
        question=request.question,
        role=current_user.role,
        top_k=request.top_k,
    )
    return {
        "question": request.question,
        "results": results,
    }
