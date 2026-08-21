from pathlib import Path

from models.file_node import FileNode
from models.folder_node import FolderNode


def test_file_node():
    file = FileNode(
        name="app.py",
        path=Path("FileManagerAI/app.py"),
        extension=".py",
        size=100,
        depth=2
    )

    assert file.name == "app.py"
    assert file.extension == ".py"


def test_folder_node():
    folder = FolderNode(
        name="FileManagerAI",
        path=Path("FileManagerAI"),
        depth=1
    )

    assert folder.name == "FileManagerAI"
    assert folder.files == []
    assert folder.children == []