from pypdf import PdfReader


def extract_text_from_pdf(file_path: str) -> list[dict]:
    """
    Extract text page-wise from a PDF.

    Returns:
        [
            {
                "page_number": 1,
                "text": "page text..."
            }
        ]
    """
    reader = PdfReader(file_path)
    pages_text = []

    for index, page in enumerate(reader.pages):
        text = page.extract_text() or ""

        cleaned_text = text.strip()

        if cleaned_text:
            pages_text.append(
                {
                    "page_number": index + 1,
                    "text": cleaned_text
                }
            )

    return pages_text