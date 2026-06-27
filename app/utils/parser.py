from pathlib import Path

from app.services.parser_service import ResumeParser


def process_single_resume(file_path: Path) -> dict:
    """
    Parse a single resume.

    This function is executed inside a ProcessPoolExecutor.
    It should not contain any database or AI logic.
    """

    text = ResumeParser.parse(file_path)

    return {
        "file_name": file_path.name,
        "raw_text": text,
    }