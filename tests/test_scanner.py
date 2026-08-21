import pytest
from pathlib import Path

from core.scanner import FileScanner


def test_scanner_invalid_path():
    scanner = FileScanner()

    with pytest.raises(FileNotFoundError):
        scanner.scan(Path("does_not_exist"))


def test_scanner_file_path(tmp_path):
    file = tmp_path / "test.txt"
    file.touch()

    scanner = FileScanner()

    with pytest.raises(NotADirectoryError):
        scanner.scan(file)