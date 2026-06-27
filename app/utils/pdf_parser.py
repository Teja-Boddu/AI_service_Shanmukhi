from pathlib import Path

from pypdf import PdfReader


def parse_pdf(file_path: Path) -> str:
    """
    Extract text from PDF.
    """

    reader = PdfReader(str(file_path))

    text = ""

    for page in reader.pages:
        extracted = page.extract_text()

        if extracted:
            text += extracted + "\n"

    return text.strip()