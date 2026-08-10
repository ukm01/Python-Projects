class PromptService:
    def build_rag_prompt(
        self,
        question: str,
        retrieved_chunks: list[dict]
    ) -> str:
        context_blocks = []

        for index, chunk in enumerate(retrieved_chunks, start=1):
            metadata = chunk["metadata"]

            context_blocks.append(
                f"""
Source {index}:
File: {metadata.get("file_name")}
Page: {metadata.get("page_number")}
Chunk: {metadata.get("chunk_index")}

Content:
{chunk["text"]}
"""
            )

        context = "\n".join(context_blocks)

        prompt = f"""
You are a document question-answering assistant.

Your job is to answer the user's question using only the provided document context.

Rules:
1. Use only the information from the context.
2. Do not use outside knowledge.
3. Do not invent facts, numbers, dates, names, or policies.
4. If the answer is not present in the context, say:
   "I don't know based on the uploaded documents."
5. Keep the answer clear and concise.
6. Mention the source page in the answer if possible.

Context:
{context}

User question:
{question}

Answer:
"""
        return prompt.strip()


prompt_service = PromptService()