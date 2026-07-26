from langchain_core.documents import Document

from app.services.ingestion.loader_factory import get_document_loader


class EmptyDocumentError(ValueError):
    pass


def load_document(file_path: str) -> list[Document]:
    loader = get_document_loader(file_path)

    documents = loader.load()

    if not documents:
        raise EmptyDocumentError(
            "No content could be extracted from the document."
        )

    return documents