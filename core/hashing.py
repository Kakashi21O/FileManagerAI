import hashlib
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class FileHasher:
    """
    Computes cryptographic file hashes using bounded streaming memory.
    Ensures safe, O(1) memory usage regardless of file size.
    """

    def __init__(self, chunk_size_mb: int = 8):
        # Default 8 MB chunk buffer
        self.chunk_size = max(1, chunk_size_mb) * 1024 * 1024

    def compute_sha256(self, file_path: Path) -> Optional[str]:
        """
        Calculates SHA-256 hash using chunked streaming.
        Returns hex digest string, or None if file cannot be read safely.
        """
        hasher = hashlib.sha256()

        try:
            with open(file_path, "rb") as f:
                while True:
                    chunk = f.read(self.chunk_size)
                    if not chunk:
                        break
                    hasher.update(chunk)
            return hasher.hexdigest()
        except (PermissionError, FileNotFoundError, OSError) as e:
            logger.warning(f"Could not hash file {file_path}: {e}")
            return None
