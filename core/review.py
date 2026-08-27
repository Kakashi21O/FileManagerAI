from pathlib import Path
from typing import Dict


class ReviewCategory:
    DUPLICATES = "Duplicates"
    SIMILAR = "Similar"
    UNCERTAIN = "Uncertain"
    EMPTY = "Empty"
    REVIEW = "Review"


class ReviewManager:
    """
    Manages the review holding area where uncertain, duplicate, or empty folders
    are placed for explicit human inspection. Never automatically deletes any files or folders.
    """

    def __init__(self, root_dir: Path, review_folder_name: str = "_FileManagerAI_Review"):
        self.root_dir = root_dir
        self.review_root = root_dir / review_folder_name

    def get_review_destination(self, source_path: Path, category: str = ReviewCategory.DUPLICATES) -> Path:
        """
        Calculates safe destination path inside the appropriate review category subfolder.
        """
        category_folder = self.review_root / category
        return category_folder / source_path.name

