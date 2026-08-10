from functools import lru_cache
from threading import Lock

from sentence_transformers import CrossEncoder

from app.config import settings


_prediction_lock = Lock()


@lru_cache(maxsize=1)
def get_reranker_model() -> CrossEncoder:
    return CrossEncoder(
        settings.RERANKER_MODEL_NAME,
        device=settings.RERANKER_DEVICE,
        max_length=settings.RERANKER_MAX_LENGTH,
    )


def score_passages(
    question: str,
    passages: list[str],
) -> list[float]:
    if not passages:
        return []

    pairs = [
        (question, passage)
        for passage in passages
    ]
    with _prediction_lock:
        scores = get_reranker_model().predict(
            pairs,
            batch_size=settings.RERANKER_BATCH_SIZE,
            show_progress_bar=False,
            convert_to_numpy=True,
        )

    return [
        float(score)
        for score in scores
    ]
