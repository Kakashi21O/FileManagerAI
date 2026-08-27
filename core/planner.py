from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Set

from core.context_engine import ContextEngine
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
    Creates an intelligent, context-aware organization plan without modifying files.
    CORE RULES:
    - Never organize a file solely because of its extension when sufficient contextual information is available.
    - Considers content, surrounding filesystem context, project boundaries, existing folder structure, and metadata.
    - If confidence is insufficient (< 0.75), do not guess. Leave untouched or route to Review/.
    """

    def __init__(
        self,
        classifier: Optional[CategoryClassifier] = None,
        detector: Optional[StructureDetector] = None,
        dup_detector: Optional[DuplicateDetector] = None,
        context_engine: Optional[ContextEngine] = None,
    ):
        self.classifier = classifier or CategoryClassifier()
        self.detector = detector or StructureDetector()
        self.dup_detector = dup_detector or DuplicateDetector()
        self.context_engine = context_engine or ContextEngine()
        self.tree_builder = TreeBuilder()

    def create_plan(self, root: FolderNode) -> OrganizationPlan:
        review_manager = ReviewManager(root.path)
        operations: List[PlanOperation] = []

        # 1. Identify protected project boundaries (never split projects!)
        project_paths: Set[Path] = set(self.detector.find_project_folders(root))

        # 2. Find exact duplicate groups
        dup_groups = self.dup_detector.find_duplicates(root)
        processed_files: Set[Path] = set()

        for group in dup_groups:
            # We preserve the original in its place, queue duplicates to review area
            for dup_path in group.duplicates:
                # Never extract duplicates from inside protected project roots
                is_in_project = any(self._is_subpath(dup_path, p) for p in project_paths)
                if not is_in_project:
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

        # 3. Contextual File Analysis & Planning
        for node in self.tree_builder.traverse(root):
            if isinstance(node, FolderNode):
                # Analyze each file in the folder with its surrounding context
                for file_node in node.files:
                    if file_node.path in processed_files:
                        continue

                    # Contextual reasoning
                    context = self.context_engine.analyze_context(file_node, node, project_paths)

                    # If inside a project or already safely structured -> stay untouched
                    if context.is_in_project:
                        continue

                    # If contextual topic was recognized with high confidence
                    if context.suggested_target_folder and context.confidence >= 0.75:
                        dest_folder = root.path / context.suggested_target_folder
                        dest_file = dest_folder / file_node.name

                        if dest_file != file_node.path and file_node.path.parent != dest_folder:
                            operations.append(
                                PlanOperation(
                                    operation_type=OperationType.MOVE,
                                    source=file_node.path,
                                    destination=dest_file,
                                    reason=context.reason,
                                    confidence=context.confidence,
                                )
                            )
                    elif file_node.path.parent == root.path:
                        # Fallback for loose top-level files: classify by category safely
                        category = self.classifier.classify(file_node.path)
                        dest_folder = root.path / category
                        dest_file = dest_folder / file_node.name

                        if dest_file != file_node.path:
                            operations.append(
                                PlanOperation(
                                    operation_type=OperationType.MOVE,
                                    source=file_node.path,
                                    destination=dest_file,
                                    reason=f"Organize loose file into {category}/ category (baseline rule)",
                                    confidence=0.75,
                                )
                            )

        return OrganizationPlan(
            operations=operations,
            duplicate_groups=dup_groups,
        )

    def _is_subpath(self, child: Path, parent: Path) -> bool:
        try:
            child.relative_to(parent)
            return True
        except ValueError:
            return False

