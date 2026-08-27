from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Set

from core.detector import StructureDetector
from core.duplicate_detector import DuplicateDetector, DuplicateGroup
from core.review import ReviewCategory, ReviewManager
from core.rules import CategoryClassifier
from core.tree_builder import TreeBuilder
from models.file_node import FileNode
from models.folder_node import FolderNode


class OperationType:
    MOVE = "MOVE"
    MOVE_TO_REVIEW = "MOVE_TO_REVIEW"


@dataclass
class PlanOperation:
    operation_type: str
    source: Path
    destination: Path
    reason: str
    confidence: float = 1.0


@dataclass
class OrganizationPlan:
    operations: List[PlanOperation]
    duplicate_groups: List[DuplicateGroup]


class OrganizationPlanner:
    """
    Creates an organization plan without modifying files.
    Respects project boundaries, groups duplicates safely into review areas,
    and categorizes stray files while avoiding unnecessary folder explosion.
    """

    def __init__(
        self,
        classifier: Optional[CategoryClassifier] = None,
        detector: Optional[StructureDetector] = None,
        dup_detector: Optional[DuplicateDetector] = None,
    ):
        self.classifier = classifier or CategoryClassifier()
        self.detector = detector or StructureDetector()
        self.dup_detector = dup_detector or DuplicateDetector()
        self.tree_builder = TreeBuilder()

    def create_plan(self, root: FolderNode) -> OrganizationPlan:
        review_manager = ReviewManager(root.path)
        operations: List[PlanOperation] = []

        # 1. Identify protected project boundaries (never split projects!)
        project_paths: Set[Path] = set(self.detector.find_project_folders(root))

        # Helper to check if a file belongs to a protected project
        def is_inside_project(p: Path) -> bool:
            for proj in project_paths:
                try:
                    p.relative_to(proj)
                    return True
                except ValueError:
                    continue
            return False

        # 2. Find exact duplicate groups
        dup_groups = self.dup_detector.find_duplicates(root)
        processed_files: Set[Path] = set()

        for group in dup_groups:
            # We preserve the original in its place, queue duplicates to review area
            for dup_path in group.duplicates:
                if not is_inside_project(dup_path):
                    review_dest = review_manager.get_review_destination(
                        dup_path, ReviewCategory.DUPLICATES
                    )
                    operations.append(
                        PlanOperation(
                            operation_type=OperationType.MOVE_TO_REVIEW,
                            source=dup_path,
                            destination=review_dest,
                            reason=f"Exact duplicate of {group.original.name} (SHA-256: {group.sha256[:8]})",
                            confidence=1.0,
                        )
                    )
                    processed_files.add(dup_path)

        # 3. Categorize unorganized direct files or top-level loose files
        for node in self.tree_builder.traverse(root):
            if isinstance(node, FileNode):
                if node.path in processed_files or is_inside_project(node.path):
                    continue

                # If the file is loose in root folder, propose moving to category folder
                if node.path.parent == root.path:
                    category = self.classifier.classify(node.path)
                    dest_folder = root.path / category
                    dest_file = dest_folder / node.path.name

                    if dest_file != node.path:
                        operations.append(
                            PlanOperation(
                                operation_type=OperationType.MOVE,
                                source=node.path,
                                destination=dest_file,
                                reason=f"Organize loose file into {category}/ category",
                                confidence=0.95,
                            )
                        )

        return OrganizationPlan(
            operations=operations,
            duplicate_groups=dup_groups,
        )
