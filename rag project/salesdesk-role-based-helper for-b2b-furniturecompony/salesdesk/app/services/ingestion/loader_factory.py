from pathlib import Path

from langchain_community.document_loaders import (
    BSHTMLLoader,
    CSVLoader,
    Docx2txtLoader,
    PyPDFLoader,
    TextLoader,
)


class UnsupportedDocumentLoaderError(ValueError):
    pass


def get_document_loader(file_path: str):
    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        return PyPDFLoader(file_path)

    if extension == ".docx":
        return Docx2txtLoader(file_path)

    if extension == ".txt":
        return TextLoader(
            file_path,
            encoding="utf-8",
            autodetect_encoding=True,
        )

    if extension in {".html", ".htm"}:
        return BSHTMLLoader(
            file_path,
            open_encoding="utf-8",
        )

    if extension == ".csv":
        return CSVLoader(file_path)

    raise UnsupportedDocumentLoaderError(
        f"No document loader configured for '{extension}'."
    )