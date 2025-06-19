import hashlib


def sha256_hash(text: str) -> str:
    """Return the SHA-256 hex digest of the given text."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()
