from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=2, max_length=2000)

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        question = value.strip()
        if len(question) < 2:
            raise ValueError("Question must contain at least 2 characters")
        return question


class LlmCitation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str


class LlmAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["answered", "insufficient_context"]
    answer: str
    citations: list[LlmCitation]


class ChatCitationResponse(BaseModel):
    source_id: str
    chunk_id: str
    document_id: int
    document_name: str
    original_filename: str
    page_number: int | None


class ChatResponse(BaseModel):
    status: Literal["answered", "insufficient_context"]
    answer: str
    citations: list[ChatCitationResponse]
    model: str
