from pathlib import Path
from typing import Optional


class FileCategory:
    CODE = "Code"
    IMAGE = "Images"
    DOCUMENT = "Documents"
    DATA = "Data"
    ARCHIVE = "Archives"
    OTHER = "Other"


class CategoryClassifier:
    """
    Classifies files into intuitive categories while respecting existing structure.
    Extensible mapping covering standard code, images, documents, and archives.
    """

    EXTENSIONS_MAP = {
        # Code & Scripts
        ".py": FileCategory.CODE,
        ".js": FileCategory.CODE,
        ".ts": FileCategory.CODE,
        ".java": FileCategory.CODE,
        ".c": FileCategory.CODE,
        ".cpp": FileCategory.CODE,
        ".h": FileCategory.CODE,
        ".hpp": FileCategory.CODE,
        ".cs": FileCategory.CODE,
        ".go": FileCategory.CODE,
        ".rs": FileCategory.CODE,
        ".php": FileCategory.CODE,
        ".html": FileCategory.CODE,
        ".css": FileCategory.CODE,
        ".sql": FileCategory.CODE,
        ".sh": FileCategory.CODE,
        ".bat": FileCategory.CODE,
        ".ps1": FileCategory.CODE,

        # Images (Level 1 exact content formats)
        ".jpg": FileCategory.IMAGE,
        ".jpeg": FileCategory.IMAGE,
        ".png": FileCategory.IMAGE,
        ".webp": FileCategory.IMAGE,
        ".gif": FileCategory.IMAGE,
        ".bmp": FileCategory.IMAGE,
        ".tiff": FileCategory.IMAGE,

        # Data & Config
        ".json": FileCategory.DATA,
        ".xml": FileCategory.DATA,
        ".yaml": FileCategory.DATA,
        ".yml": FileCategory.DATA,
        ".toml": FileCategory.DATA,
        ".csv": FileCategory.DATA,

        # Documents
        ".md": FileCategory.DOCUMENT,
        ".txt": FileCategory.DOCUMENT,
        ".pdf": FileCategory.DOCUMENT,
        ".docx": FileCategory.DOCUMENT,

        # Archives
        ".zip": FileCategory.ARCHIVE,
        ".rar": FileCategory.ARCHIVE,
        ".7z": FileCategory.ARCHIVE,
        ".tar": FileCategory.ARCHIVE,
        ".gz": FileCategory.ARCHIVE,
    }

    def classify(self, path: Path) -> str:
        """
        Returns the category name based on file extension.
        """
        ext = path.suffix.lower()
        return self.EXTENSIONS_MAP.get(ext, FileCategory.OTHER)
