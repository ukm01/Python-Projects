@router.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):
    try:
        retrieved_chunks = retrieval_service.retrieve_relevant_chunks(
            question=request.question,
            top_k=request.top_k
        )

        prompt = prompt_service.build_rag_prompt(
            question=request.question,
            retrieved_chunks=retrieved_chunks
        )

        answer = llm_service.generate_answer(prompt)

        is_no_answer = "i don't know based on the uploaded documents" in answer.lower()

        sources = []

        if not is_no_answer:
            for chunk in retrieved_chunks:
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
            "retrieved_chunks_count": len(retrieved_chunks)
        }

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error while answering question: {str(error)}"
        )