from pathlib import Path
from zipfile import ZipFile

from app.core.config import settings


class ZipService:

    @staticmethod
    def extract(
        zip_path: Path,
        job_id: str,
    ) -> list[Path]:
        """
        Extract resumes into a job-specific folder.
        """

        extract_dir = (
            Path(settings.EXTRACT_DIR)
            / job_id
        )

        extract_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        with ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)

        resumes = []

        for file in extract_dir.rglob("*"):

            if file.suffix.lower() in [
                ".pdf",
                ".docx",
            ]:
                resumes.append(file)

        return resumes