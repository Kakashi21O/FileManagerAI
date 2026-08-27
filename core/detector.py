from pathlib import Path
from typing import List
from models.folder_node import FolderNode
from core.tree_builder import TreeBuilder


class StructureDetector:
    """Detects structural patterns and issues in a folder tree."""

    def __init__(self, max_allowed_depth: int = 4):
        self.builder = TreeBuilder()
        self.max_allowed_depth = max_allowed_depth
        # Standard indicators for known project/codebase directories
        self.project_indicators = {
            "package.json",
            "pyproject.toml",
            "setup.py",
            "requirements.txt",
            "Cargo.toml",
            "pom.xml",
            "build.gradle",
            "go.mod",
            ".git",
        }

    def find_empty_folders(self, root: FolderNode) -> List[Path]:
        """
        Finds folders that contain no direct files and no child folders.
        """
        empty_folders: List[Path] = []
        for node in self.builder.traverse(root):
            if isinstance(node, FolderNode):
                if len(node.files) == 0 and len(node.children) == 0:
                    empty_folders.append(node.path)
        return empty_folders

    def find_redundant_nesting(self, root: FolderNode) -> List[Path]:
        """
        Detects 'single-child' redundant chains in subfolders:
        A non-root folder that has 0 files and exactly 1 child folder (e.g., A/ -> B/ -> ...).
        """
        redundant: List[Path] = []
        for node in self.builder.traverse(root):
            if isinstance(node, FolderNode):
                # We skip the root folder itself since the selected root directory is user-provided
                if node != root and len(node.files) == 0 and len(node.children) == 1:
                    redundant.append(node.path)
        return redundant


    def find_deep_folders(self, root: FolderNode) -> List[Path]:
        """
        Finds folders whose depth exceeds the maximum allowed depth.
        """
        deep_folders: List[Path] = []
        for node in self.builder.traverse(root):
            if isinstance(node, FolderNode):
                if node.depth > self.max_allowed_depth:
                    deep_folders.append(node.path)
        return deep_folders

    def find_project_folders(self, root: FolderNode) -> List[Path]:
        """
        Identifies potential standalone project directories based on marker files.
        """
        projects: List[Path] = []
        for node in self.builder.traverse(root):
            if isinstance(node, FolderNode):
                file_names = {f.name for f in node.files}
                if file_names.intersection(self.project_indicators):
                    projects.append(node.path)
        return projects
