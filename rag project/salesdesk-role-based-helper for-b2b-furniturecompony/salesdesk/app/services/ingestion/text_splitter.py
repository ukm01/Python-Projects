from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=120,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def split_documents(
    documents: list[Document],
) -> list[Document]:
    return text_splitter.split_documents(documents)