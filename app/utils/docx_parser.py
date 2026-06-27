from pathlib import Path

from docx import Document


def parse_docx(file_path: Path) -> str:
    """
    Extract text from DOCX.
    """

    document = Document(str(file_path))

    text = []

    for para in document.paragraphs:
        text.append(para.text)

    return "\n".join(text).strip()