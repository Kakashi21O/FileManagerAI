from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

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
    """

    def __init__(self, hasher: Optional[FileHasher] = None, tree_builder: Optional[TreeBuilder] = None):
        self.hasher = hasher or FileHasher()
        self.tree_builder = tree_builder or TreeBuilder()

    def find_duplicates(self, root: FolderNode) -> List[DuplicateGroup]:
        """
        Scans all files in the tree and groups exact duplicates.
        """
        # Step 1: Group files by byte size (O(n) grouping)
        size_groups: Dict[int, List[FileNode]] = defaultdict(list)

        for node in self.tree_builder.traverse(root):
            if isinstance(node, FileNode):
                # 0-byte files can be ignored or grouped, but usually files > 0 bytes are duplicates
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
                    # Deterministically pick the first path (or shortest depth) as original
                    original = paths[0]
                    duplicates = paths[1:]
                    duplicate_groups.append(
                        DuplicateGroup(
                            sha256=sha256,
                            size=size,
                            original=original,
                            duplicates=duplicates,
                        )
                    )

        return duplicate_groups
