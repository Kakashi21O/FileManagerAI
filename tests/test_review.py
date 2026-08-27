from pathlib import Path
from core.review import ReviewManager, ReviewCategory


def test_review_manager_paths(tmp_path):
    manager = ReviewManager(tmp_path)
    source = tmp_path / "downloads" / "duplicate_img.png"

    dup_dest = manager.get_review_destination(source, ReviewCategory.DUPLICATES)
    assert dup_dest == tmp_path / "_FileManagerAI_Review" / "Duplicates" / "duplicate_img.png"

    similar_dest = manager.get_review_destination(source, ReviewCategory.SIMILAR)
    assert similar_dest == tmp_path / "_FileManagerAI_Review" / "Similar" / "duplicate_img.png"
