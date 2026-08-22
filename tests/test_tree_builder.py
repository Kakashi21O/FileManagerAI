from pathlib import Path

from core.scanner import FileScanner
from core.tree_builder import TreeBuilder


def test_tree_builder():
    root_path = Path("models")

    scanner = FileScanner({})
    root = scanner.scan(root_path)

    builder = TreeBuilder()
    result = builder.build(root)

    assert result is root
    assert result.name == "models"