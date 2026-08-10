from app.config import settings


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """
    Simple character-based chunking.

    Later we will replace this with token-aware chunking.
    """
    if not text:
        return []

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start = end - chunk_overlap

    return chunks


def chunk_pages(pages_text: list[dict]) -> list[dict]:
    """
    Convert page-wise text into chunks with metadata.

    Returns:
        [
            {
                "chunk_index": 0,
                "page_number": 1,
                "text": "chunk text..."
            }
        ]
    """
    all_chunks = []
    chunk_index = 0

    for page in pages_text:
        page_number = page["page_number"]
        text = page["text"]

        page_chunks = chunk_text(
            text=text,
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )

        for chunk in page_chunks:
            all_chunks.append(
                {
                    "chunk_index": chunk_index,
                    "page_number": page_number,
                    "text": chunk
                }
            )
            chunk_index += 1

    return all_chunks