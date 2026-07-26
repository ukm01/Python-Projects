from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user_model import User
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.security.dependencies import get_current_user
from app.services.chat_service import ChatService


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)

chat_service = ChatService()


@router.post(
    "/ask",
    response_model=ChatResponse,
)
def ask_question(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return chat_service.ask(
        db=db,
        user_id=current_user.id,
        role=current_user.role,
        question=request.question,
    )
