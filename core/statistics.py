from models.folder_node import FolderNode
from models.file_node import FileNode
from models.scan_result import ScanResult
from core.tree_builder import TreeBuilder


class FolderStatistics:
    """Calculates summary statistics for a folder tree."""

    def __init__(self):
        self.builder = TreeBuilder()

    def calculate(self, root: FolderNode) -> ScanResult:
        """
        Calculates total files, total folders, and total file size across the tree.
        """
        total_files = 0
        total_folders = 0
        total_size = 0

        # Traverse the entire hierarchy using TreeBuilder's generator
        for node in self.builder.traverse(root):
            if isinstance(node, FolderNode):
                total_folders += 1
            elif isinstance(node, FileNode):
                total_files += 1
                total_size += node.size

        return ScanResult(
            root=root,
            total_files=total_files,
            total_folders=total_folders,
            total_size=total_size,
        )
