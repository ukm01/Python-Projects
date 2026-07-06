import os
import uuid
from fastapi import UploadFile


def ensure_directory_exists(directory_path: str) -> None:
    os.makedirs(directory_path, exist_ok=True)


def validate_pdf_file(file: UploadFile) -> None:
    if not file.filename:
        raise ValueError("File name is missing.")

    if not file.filename.lower().endswith(".pdf"):
        raise ValueError("Only PDF files are allowed.")


def generate_unique_file_name(original_file_name: str) -> str:
    file_extension = original_file_name.split(".")[-1]
    unique_id = str(uuid.uuid4())
    return f"{unique_id}.{file_extension}"


async def save_uploaded_file(file: UploadFile, upload_dir: str) -> str:
    ensure_directory_exists(upload_dir)

    unique_file_name = generate_unique_file_name(file.filename)
    file_path = os.path.join(upload_dir, unique_file_name)

    content = await file.read()

    with open(file_path, "wb") as buffer:
        buffer.write(content)

    return file_path