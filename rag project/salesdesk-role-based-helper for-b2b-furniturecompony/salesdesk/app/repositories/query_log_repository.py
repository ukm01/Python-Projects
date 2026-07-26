import json

from sqlalchemy.orm import Session

from app.models.query_log_model import QueryLog


class QueryLogRepository:

    def create(
        self,
        db: Session,
        user_id: int,
        question: str,
        answer: str,
        sources: list[dict],
    ) -> None:
        db.add(
            QueryLog(
                user_id=user_id,
                question=question,
                answer=answer,
                sources=json.dumps(sources),
            )
        )
        db.commit()
