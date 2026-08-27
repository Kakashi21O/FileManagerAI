from pathlib import Path
from core.scanner import FileScanner
from core.duplicate_detector import DuplicateDetector


def test_duplicate_detector_finds_exact_duplicates(tmp_path):
    # Setup test files
    file1 = tmp_path / "orig.txt"
    file1.write_text("Unique text content 12345")

    sub = tmp_path / "sub"
    sub.mkdir()
    file2 = sub / "copy.txt"
    file2.write_text("Unique text content 12345")  # Identical content

    other = tmp_path / "other.txt"
    other.write_text("Different content, same length!")

    scanner = FileScanner({})
    root = scanner.scan(tmp_path)

    detector = DuplicateDetector()
    groups = detector.find_duplicates(root)

    assert len(groups) == 1
    assert groups[0].original == file1
    assert groups[0].duplicates == [file2]
    assert groups[0].size == len("Unique text content 12345")


def test_duplicate_detector_no_duplicates(tmp_path):
    (tmp_path / "a.txt").write_text("aaa")
    (tmp_path / "b.txt").write_text("bbb")

    scanner = FileScanner({})
    root = scanner.scan(tmp_path)

    detector = DuplicateDetector()
    groups = detector.find_duplicates(root)

    assert len(groups) == 0
