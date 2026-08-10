import json
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.document_chunk_model import DocumentChunk
from app.models.document_model import Document as DocumentModel
from app.services.ingestion.document_loader import load_document
from app.services.ingestion.document_processor import prepare_documents
from app.services.ingestion.text_splitter import split_documents
from app.services.ingestion.vector_store import delete_vector_ids, vector_store


def ingest_document(
    db: Session,
    document_record: DocumentModel,
) -> list[str]:
    documents = load_document(
        document_record.file_path
    )

    prepared_documents = prepare_documents(
        documents=documents,
        document_record=document_record,
    )

    chunks = split_documents(
        prepared_documents
    )

    vector_ids: list[str] = []
    chunk_rows: list[DocumentChunk] = []

    for chunk_index, chunk in enumerate(chunks):
        chunk_id = str(uuid4())
        page_number = _get_page_number(chunk.metadata)
        metadata = _json_safe_metadata(chunk.metadata)

        metadata.update(
            {
                "chunk_id": chunk_id,
                "vector_id": chunk_id,
                "chunk_index": chunk_index,
            }
        )
        chunk.metadata = metadata
        vector_ids.append(chunk_id)
        chunk_rows.append(
            DocumentChunk(
                chunk_id=chunk_id,
                document_id=document_record.id,
                vector_id=chunk_id,
                content=chunk.page_content,
                page_number=page_number,
                chunk_index=chunk_index,
                chunk_metadata=metadata,
            )
        )

    vector_store.add_documents(
        documents=chunks,
        ids=vector_ids,
    )

    try:
        db.add_all(chunk_rows)
        db.flush()
    except Exception:
        delete_vector_ids(vector_ids)
        raise

    return vector_ids


def _get_page_number(metadata: dict) -> int | None:
    page = metadata.get("page")

    if isinstance(page, int):
        return page + 1

    page_label = metadata.get("page_label")

    if isinstance(page_label, str) and page_label.isdigit():
        return int(page_label)

    return None


def _json_safe_metadata(metadata: dict) -> dict:
    return json.loads(
        json.dumps(metadata, default=str)
    )
