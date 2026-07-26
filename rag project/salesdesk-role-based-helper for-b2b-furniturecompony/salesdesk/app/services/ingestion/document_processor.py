from langchain_core.documents import Document

from app.models.document_model import Document as DocumentModel


def prepare_documents(
    documents: list[Document],
    document_record: DocumentModel,
) -> list[Document]:

    prepared_documents: list[Document] = []

    for document in documents:
        document.metadata.update(
            {
                "document_id": document_record.id,
                "document_name": document_record.document_name,
                "category": document_record.category,
                "product_name": document_record.product_name,
                "original_filename": document_record.original_filename,
            }
        )

        prepared_documents.append(document)

    return prepared_documents