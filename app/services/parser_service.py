from pathlib import Path

from app.utils.docx_parser import parse_docx
from app.utils.pdf_parser import parse_pdf


class ResumeParser:

    @staticmethod
    def parse(file_path: Path) -> str:

        suffix = file_path.suffix.lower()

        if suffix == ".pdf":
            return parse_pdf(file_path)

        elif suffix == ".docx":
            return parse_docx(file_path)

        raise ValueError(f"Unsupported file type: {suffix}")