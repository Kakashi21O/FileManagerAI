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

        # 3. Structural & Folder Unit Planning
        # Top-level direct subdirectories under root
        for child_folder in root.children:
            # If the child folder is an identified project or coherent unit, determine if its location needs organizing
            folder_path = child_folder.path
            
            # Check if this top-level folder already matches standard category names (e.g. Python, Web, Code, etc.)
            if folder_path.name in {"Python", "Web", "Code", "Images", "Documents", "Data", "Archives", "_FileManagerAI_Review"}:
                continue

            # Check if all files/subfolders indicate a specific topic (e.g. Python project, Web frontend project)
            # Find majority topic across files inside this folder unit
            folder_files = []
            for n in self.tree_builder.traverse(child_folder):
                if isinstance(n, FileNode):
                    folder_files.append(n)

            # Analyze files inside the folder unit to decide where the whole folder belongs
            if folder_files:
                sample_contexts = [
                    self.context_engine.analyze_context(f, child_folder, project_paths)
                    for f in folder_files[:10]  # Sample first 10 files
                ]
                
                # Check for cohesive target suggestion
                topics = [c.suggested_target_folder for c in sample_contexts if c.suggested_target_folder]
                if topics:
                    # Pick most common target folder (e.g., Python/AI or Web/Frontend)
                    dominant_target = max(set(topics), key=topics.count)
                    dest_parent = root.path / dominant_target
                    dest_folder = dest_parent / folder_path.name

                    if dest_folder.resolve() != folder_path.resolve() and folder_path.parent.resolve() != dest_parent.resolve():
                        operations.append(
                            PlanOperation(
                                operation_type=OperationType.MOVE,
                                source=folder_path,
                                destination=dest_folder,
                                reason=f"Move entire coherent folder unit into {dominant_target}/",
                                confidence=0.85,
                            )
                        )
                        # Mark all files in this whole folder as processed so we don't move individual internal files
                        for f in folder_files:
                            processed_files.add(f.path)

        # 4. Only loose, orphaned top-level files are categorized individually
        for file_node in root.files:
            if file_node.path in processed_files:
                continue

            context = self.context_engine.analyze_context(file_node, root, project_paths)
            if context.suggested_target_folder and context.confidence >= 0.75:
                dest_folder = root.path / context.suggested_target_folder
                dest_file = dest_folder / file_node.name
                if dest_file != file_node.path:
                    operations.append(
                        PlanOperation(
                            operation_type=OperationType.MOVE,
                            source=file_node.path,
                            destination=dest_file,
                            reason=context.reason,
                            confidence=context.confidence,
                        )
                    )
            else:
                category = self.classifier.classify(file_node.path)
                dest_folder = root.path / category
                dest_file = dest_folder / file_node.name
                if dest_file != file_node.path:
                    operations.append(
                        PlanOperation(
                            operation_type=OperationType.MOVE,
                            source=file_node.path,
                            destination=dest_file,
                            reason=f"Organize loose root file into {category}/",
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

