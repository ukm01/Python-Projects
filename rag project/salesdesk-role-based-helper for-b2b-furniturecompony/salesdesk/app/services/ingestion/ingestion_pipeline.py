from app.models.document_model import Document as DocumentModel
from app.services.ingestion.document_loader import load_document
from app.services.ingestion.document_processor import prepare_documents
from app.services.ingestion.text_splitter import split_documents
from app.services.ingestion.vector_store import vector_store


def ingest_document(
    document_record: DocumentModel,
) -> int:
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

    vector_store.add_documents(
        documents=chunks
    )

    return len(chunks)