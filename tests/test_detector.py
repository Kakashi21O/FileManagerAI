from pathlib import Path
from core.scanner import FileScanner
from core.detector import StructureDetector


def test_detector_empty_folders(tmp_path):
    empty_sub = tmp_path / "empty_dir"
    empty_sub.mkdir()

    non_empty = tmp_path / "has_file"
    non_empty.mkdir()
    (non_empty / "a.txt").touch()

    scanner = FileScanner({})
    root = scanner.scan(tmp_path)

    detector = StructureDetector()
    empty_dirs = detector.find_empty_folders(root)

    assert empty_dirs == [empty_sub]


def test_detector_redundant_nesting(tmp_path):
    # Setup chain: root -> single_child -> target -> file.txt
    single_child = tmp_path / "single_child"
    single_child.mkdir()

    target = single_child / "target"
    target.mkdir()
    (target / "doc.txt").touch()

    scanner = FileScanner({})
    root = scanner.scan(tmp_path)

    detector = StructureDetector()
    redundant = detector.find_redundant_nesting(root)

    # single_child has 0 files and 1 folder (target)
    assert redundant == [single_child]


def test_detector_deep_folders(tmp_path):
    # Depth 0: tmp_path
    # Depth 1: d1
    # Depth 2: d2
    # Depth 3: d3
    d1 = tmp_path / "d1"
    d1.mkdir()
    d2 = d1 / "d2"
    d2.mkdir()
    d3 = d2 / "d3"
    d3.mkdir()

    scanner = FileScanner({})
    root = scanner.scan(tmp_path)

    # Max allowed depth = 2, so d3 (depth 3) should be flagged
    detector = StructureDetector(max_allowed_depth=2)
    deep = detector.find_deep_folders(root)

    assert deep == [d3]


def test_detector_project_folders(tmp_path):
    proj = tmp_path / "my_project"
    proj.mkdir()
    (proj / "package.json").touch()

    normal = tmp_path / "notes"
    normal.mkdir()
    (normal / "notes.txt").touch()

    scanner = FileScanner({})
    root = scanner.scan(tmp_path)

    detector = StructureDetector()
    projects = detector.find_project_folders(root)

    assert projects == [proj]
