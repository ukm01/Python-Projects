from pydantic import BaseModel, ConfigDict, Field, field_validator


class RetrievalRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=2, max_length=2000)
    top_k: int = Field(default=8, ge=1, le=20)

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        question = value.strip()
        if len(question) < 2:
            raise ValueError("Question must contain at least 2 characters")
        return question


class RetrievedChunkResponse(BaseModel):
    chunk_id: str
    document_id: int
    document_name: str
    original_filename: str
    category: str
    page_number: int | None
    chunk_index: int
    content: str
    score: float
    hybrid_score: float
    reranker_score: float
    reranker_rank: int
    match_types: list[str]
    vector_rank: int | None
    keyword_rank: int | None
    vector_distance: float | None
    keyword_score: float | None


class RetrievalResponse(BaseModel):
    question: str
    results: list[RetrievedChunkResponse]
