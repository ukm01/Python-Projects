import uuid
from fastapi import UploadFile

from app.config import settings
from app.utils.file_utils import validate_pdf_file, save_uploaded_file
from app.services.extraction_service import extract_text_from_pdf
from app.services.chunking_service import chunk_pages
from app.services.embedding_service import embedding_service
from app.services.vector_store_service import vector_store_service


class DocumentService:
    async def upload_and_index_document(self, file: UploadFile) -> dict:
        validate_pdf_file(file)

        document_id = str(uuid.uuid4())

        file_path = await save_uploaded_file(
            file=file,
            upload_dir=settings.UPLOAD_DIR
        )

        pages_text = extract_text_from_pdf(file_path)

        if not pages_text:
            raise ValueError(
                "No extractable text found in the PDF. It may be scanned or image-based."
            )

        chunks = chunk_pages(pages_text)

        if not chunks:
            raise ValueError("No chunks created from the document.")

        chunk_texts = [chunk["text"] for chunk in chunks]

        embeddings = embedding_service.embed_texts(chunk_texts)

        stored_chunk_count = vector_store_service.add_chunks(
            document_id=document_id,
            file_name=file.filename,
            chunks=chunks,
            embeddings=embeddings
        )

        return {
            "document_id": document_id,
            "file_name": file.filename,
            "saved_file_path": file_path,
            "total_pages_with_text": len(pages_text),
            "total_chunks": stored_chunk_count,
            "status": "indexed",
            "message": "Document uploaded, extracted, chunked, embedded, and stored in ChromaDB."
        }


document_service = DocumentService()