from pathlib import Path
import pytest

from core.scanner import FileScanner
from core.tree_builder import TreeBuilder
from models.file_node import FileNode
from models.folder_node import FolderNode


def test_tree_builder():
    root_path = Path("models")

    scanner = FileScanner({})
    root = scanner.scan(root_path)

    builder = TreeBuilder()
    result = builder.build(root)

    assert result is root
    assert result.name == "models"


def test_tree_builder_detects_wrong_file_parent(tmp_path):
    root = FolderNode(
        name="root",
        path=tmp_path,
        depth=0
    )

    wrong_file = FileNode(
        name="test.txt",
        path=tmp_path / "wrong" / "test.txt",
        extension=".txt",
        size=10,
        depth=1
    )

    root.files.append(wrong_file)

    builder = TreeBuilder()

    with pytest.raises(ValueError):
        builder.build(root)


def test_tree_builder_traverse(tmp_path):
    # Setup test folder structure on disk
    (tmp_path / "file1.txt").touch()

    sub_folder = tmp_path / "folder"
    sub_folder.mkdir()
    (sub_folder / "file2.py").touch()

    nested_folder = sub_folder / "sub"
    nested_folder.mkdir()
    (nested_folder / "file3.pdf").touch()

    # Scan to build our node tree
    scanner = FileScanner({})
    root = scanner.scan(tmp_path)

    builder = TreeBuilder()
    # Collect all visited nodes during traversal
    traversed_items = list(builder.traverse(root))
    traversed_names = [item.name for item in traversed_items]

    # Verify the preorder traversal order: root -> file1.txt -> folder -> file2.py -> sub -> file3.pdf
    expected_names = [
        tmp_path.name,
        "file1.txt",
        "folder",
        "file2.py",
        "sub",
        "file3.pdf"
    ]

    assert traversed_names == expected_names