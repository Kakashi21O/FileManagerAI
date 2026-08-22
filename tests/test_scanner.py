from pathlib import Path

import pytest

from core.scanner import FileScanner


def test_scanner(tmp_path):
    # Create test structure
    (tmp_path / "file1.txt").touch()

    folder1 = tmp_path / "folder1"
    folder1.mkdir()

    (folder1 / "file2.py").touch()

    folder2 = folder1 / "folder2"
    folder2.mkdir()

    (folder2 / "file3.pdf").touch()

    folder3 = tmp_path / "folder3"
    folder3.mkdir()

    # Scan
    scanner = FileScanner({})
    root = scanner.scan(tmp_path)

    # Root
    assert root.name == tmp_path.name
    assert len(root.files) == 1
    assert len(root.children) == 2

    # folder1
    folder1_node = next(
        folder for folder in root.children
        if folder.name == "folder1"
    )

    assert len(folder1_node.files) == 1
    assert folder1_node.files[0].name == "file2.py"
    assert folder1_node.depth == 1

    # folder2
    folder2_node = next(
        folder for folder in folder1_node.children
        if folder.name == "folder2"
    )

    assert len(folder2_node.files) == 1
    assert folder2_node.files[0].name == "file3.pdf"
    assert folder2_node.depth == 2


def test_scanner_invalid_path():
    scanner = FileScanner({})

    with pytest.raises(FileNotFoundError):
        scanner.scan(Path("does_not_exist"))


def test_scanner_file_path(tmp_path):
    file = tmp_path / "test.txt"
    file.touch()

    scanner = FileScanner({})

    with pytest.raises(NotADirectoryError):
        scanner.scan(file)
        
def test_scanner_ignores_configured_folders(tmp_path):
    (tmp_path / "file.txt").touch()

    ignored_folder = tmp_path / "__pycache__"
    ignored_folder.mkdir()

    (ignored_folder / "cache.pyc").touch()

    config = {
        "ignore": ["__pycache__"]
    }

    scanner = FileScanner(config)
    root = scanner.scan(tmp_path)

    assert len(root.files) == 1
    assert len(root.children) == 0