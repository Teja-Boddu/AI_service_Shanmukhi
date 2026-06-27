import hashlib


def generate_hash(text: str) -> str:
    """
    Generate SHA256 hash for resume text.
    Used for duplicate detection.
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()