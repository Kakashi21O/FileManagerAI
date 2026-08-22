from pathlib import Path

from models.file_node import FileNode
from models.folder_node import FolderNode


class FileScanner:

    def __init__(self, config: dict):
        self.config = config
        self.ignore = set(config.get("ignore", []))

    def scan(self, path: Path) -> FolderNode:
        if not path.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")

        if not path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {path}")

        return self._scan_folder(path, depth=0)

    def _scan_folder(self, path: Path, depth: int) -> FolderNode:
        folder = FolderNode(
            name=path.name,
            path=path,
            depth=depth
        )

        for item in path.iterdir():

            if item.name in self.ignore:
                continue

            if item.is_file():
                file = FileNode(
                    name=item.name,
                    path=item,
                    extension=item.suffix,
                    size=item.stat().st_size,
                    depth=depth + 1
                )

                folder.files.append(file)

            elif item.is_dir():
                child_folder = self._scan_folder(
                    item,
                    depth + 1
                )

                folder.children.append(child_folder)

        return folder