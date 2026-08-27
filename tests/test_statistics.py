from pathlib import Path
from core.scanner import FileScanner
from core.statistics import FolderStatistics


def test_folder_statistics(tmp_path):
    # Setup files with known sizes
    file1 = tmp_path / "file1.txt"
    file1.write_text("hello")  # 5 bytes

    sub = tmp_path / "sub"
    sub.mkdir()

    file2 = sub / "file2.txt"
    file2.write_text("world!")  # 6 bytes

    scanner = FileScanner({})
    root = scanner.scan(tmp_path)

    stats = FolderStatistics()
    result = stats.calculate(root)

    assert result.root == root
    assert result.total_folders == 2  # tmp_path root + sub folder
    assert result.total_files == 2
    assert result.total_size == 11
