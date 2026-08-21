from pathlib import Path

from models.file_node import FileNode
from models.folder_node import FolderNode


class FileScanner:

    def scan(self, path: Path):
        if not path.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")

        if not path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {path}")

        files = []
        folders = []

        for item in path.iterdir():
            if item.is_file():
                file = FileNode(
                    name=item.name,
                    path=item,
                    extension=item.suffix,
                    size=item.stat().st_size,
                    depth=1
                )
                files.append(file)

            elif item.is_dir():
                folder = FolderNode(
                    name=item.name,
                    path=item,
                    depth=1
                )
                folders.append(folder)

        return files, folders