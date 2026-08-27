from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set

from core.hashing import FileHasher
from core.tree_builder import TreeBuilder
from models.file_node import FileNode
from models.folder_node import FolderNode


@dataclass
class DuplicateGroup:
    """Represents a set of identical duplicate files."""
    sha256: str
    size: int
    original: Path
    duplicates: List[Path]


class DuplicateDetector:
    """
    Finds exact duplicate files efficiently.
    Uses candidate grouping (size -> hash) to achieve O(n) average complexity
    and avoid unnecessary O(n^2) comparisons.

    Rules:
    - Skips empty (0-byte) files — they are not meaningful duplicates.
    - Skips files inside known project boundaries (intentional asset sets).
    - Never hashes directories.
    """

    def __init__(self, hasher: Optional[FileHasher] = None, tree_builder: Optional[TreeBuilder] = None):
        self.hasher = hasher or FileHasher()
        self.tree_builder = tree_builder or TreeBuilder()

    def _in_project(self, path: Path, project_paths: Set[Path]) -> bool:
        for proj in project_paths:
            try:
                path.relative_to(proj)
                return True
            except ValueError:
                continue
        return False

    def find_duplicates(
        self,
        root: FolderNode,
        project_paths: Optional[Set[Path]] = None,
    ) -> List[DuplicateGroup]:
        """
        Scans all files in the tree and groups exact duplicates.
        Excludes: empty files, directories, and files inside project roots.
        """
        protected = project_paths or set()

        # Step 1: Group files by byte size (O(n) grouping)
        size_groups: Dict[int, List[FileNode]] = defaultdict(list)

        for node in self.tree_builder.traverse(root):
            if not isinstance(node, FileNode):
                continue
            # Safety: must be an actual file on disk, not a directory
            if not node.path.is_file():
                continue
            # Skip empty files — not meaningful duplicates; handled by optimizer as Empty
            if node.size == 0:
                continue
            # Skip files inside protected project roots (intentional assets, icon packs, etc.)
            if self._in_project(node.path, protected):
                continue

            size_groups[node.size].append(node)

        duplicate_groups: List[DuplicateGroup] = []

        # Step 2: For sizes with 2+ candidates, compute chunked SHA-256
        for size, candidate_files in size_groups.items():
            if len(candidate_files) < 2:
                continue

            hash_groups: Dict[str, List[Path]] = defaultdict(list)
            for file_node in candidate_files:
                file_hash = self.hasher.compute_sha256(file_node.path)
                if file_hash:
                    hash_groups[file_hash].append(file_node.path)

            # Step 3: Any hash group with 2+ files is an exact duplicate set
            for sha256, paths in hash_groups.items():
                if len(paths) >= 2:
                    # Pick the shallowest (least nested) path as the original to keep
                    sorted_paths = sorted(paths, key=lambda p: len(p.parts))
                    original = sorted_paths[0]
                    duplicates = sorted_paths[1:]
                    duplicate_groups.append(
                        DuplicateGroup(
                            sha256=sha256,
                            size=size,
                            original=original,
                            duplicates=duplicates,
                        )
                    )

        return duplicate_groups
