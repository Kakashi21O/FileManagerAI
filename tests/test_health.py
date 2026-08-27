from core.scanner import FileScanner
from core.health import FolderHealth


def test_folder_health_clean_tree(tmp_path):
    # A clean structure
    sub = tmp_path / "src"
    sub.mkdir()
    (sub / "main.py").touch()

    scanner = FileScanner({})
    root = scanner.scan(tmp_path)

    health = FolderHealth()
    report = health.evaluate(root)

    assert report.score == 100
    assert len(report.issues_found) == 0


def test_folder_health_with_issues(tmp_path):
    # Empty folder
    (tmp_path / "empty1").mkdir()

    # Redundant chain: redundant_parent -> child -> file.txt
    redundant_parent = tmp_path / "redundant_parent"
    redundant_parent.mkdir()
    child = redundant_parent / "child"
    child.mkdir()
    (child / "file.txt").touch()

    scanner = FileScanner({})
    root = scanner.scan(tmp_path)

    health = FolderHealth()
    report = health.evaluate(root)

    assert report.score < 100
    assert len(report.issues_found) >= 2
