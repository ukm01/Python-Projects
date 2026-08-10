from fastapi import APIRouter, HTTPException, status

from app.schemas.query_schema import (
    RetrieveRequest,
    RetrieveResponse,
    AskRequest,
    AskResponse
)
from app.services.retrieval_service import retrieval_service
from app.services.prompt_service import prompt_service
from app.services.llm_service import llm_service


router = APIRouter(
    prefix="/query",
    tags=["Query"]
)


@router.post("/retrieve", response_model=RetrieveResponse)
def retrieve_chunks(request: RetrieveRequest):
    try:
        results = retrieval_service.retrieve_relevant_chunks(
            question=request.question,
            top_k=request.top_k
        )

        return {
            "question": request.question,
            "top_k": request.top_k,
            "results": results
        }

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error while retrieving chunks: {str(error)}"
        )


@router.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):
    try:
        retrieved_chunks = retrieval_service.retrieve_relevant_chunks(
            question=request.question,
            top_k=request.top_k
        )

        retrieval_confident = retrieval_service.is_retrieval_confident(
            retrieved_chunks=retrieved_chunks
        )

        if not retrieval_confident:
            return {
                "question": request.question,
                "answer": "I don't know based on the uploaded documents.",
                "sources": [],
                "retrieved_chunks_count": len(retrieved_chunks),
                "used_chunks_count": 0,
                "retrieval_confident": False
            }

        filtered_chunks = retrieval_service.filter_chunks_by_distance(
            retrieved_chunks=retrieved_chunks
        )

        prompt = prompt_service.build_rag_prompt(
            question=request.question,
            retrieved_chunks=filtered_chunks
        )

        answer = llm_service.generate_answer(prompt)

        is_no_answer = "i don't know based on the uploaded documents" in answer.lower()

        sources = []

        if not is_no_answer:
            for chunk in filtered_chunks:
                metadata = chunk["metadata"]

                sources.append(
                    {
                        "file_name": metadata.get("file_name"),
                        "page_number": metadata.get("page_number"),
                        "chunk_index": metadata.get("chunk_index")
                    }
                )

        return {
            "question": request.question,
            "answer": answer,
            "sources": sources,
            "retrieved_chunks_count": len(retrieved_chunks),
            "used_chunks_count": len(filtered_chunks),
            "retrieval_confident": True
        }

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error while answering question: {str(error)}"
        )