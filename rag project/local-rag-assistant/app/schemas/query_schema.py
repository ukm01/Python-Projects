from pydantic import BaseModel, Field


class RetrieveRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=3, ge=1, le=10)


class RetrievedChunk(BaseModel):
    text: str
    metadata: dict
    distance: float


class RetrieveResponse(BaseModel):
    question: str
    top_k: int
    results: list[RetrievedChunk]


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=3, ge=1, le=10)


class Source(BaseModel):
    file_name: str | None = None
    page_number: int | None = None
    chunk_index: int | None = None


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[Source]
    retrieved_chunks_count: int
    used_chunks_count: int
    retrieval_confident: bool