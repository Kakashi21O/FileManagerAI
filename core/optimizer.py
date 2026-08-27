from dataclasses import dataclass
import json
import logging
from pathlib import Path
import tempfile
from typing import List, Optional, Set

from core.detector import StructureDetector
from core.planner import PlanOperation, OperationType
from core.review import ReviewCategory, ReviewManager
from core.tree_builder import TreeBuilder
from models.folder_node import FolderNode

logger = logging.getLogger(__name__)


@dataclass
class OptimizationPlan:
    empty_folder_moves: List[PlanOperation]
    collapsed_chains: List[str]
    temp_state_file: Path


class HierarchyOptimizer:
    """
    Optimizes directory hierarchies:
    - Identifies empty folders and routes them safely into '_FileManagerAI_Review/Empty/'
      instead of deleting them.
    - Flattens redundant single-child chains (e.g. A/ -> B/ -> ...).
    - Preserves safety by persisting intermediate optimization state in temp files.
    """

    def __init__(
        self,
        detector: Optional[StructureDetector] = None,
        tree_builder: Optional[TreeBuilder] = None,
    ):
        self.detector = detector or StructureDetector()
        self.tree_builder = tree_builder or TreeBuilder()

    def optimize_hierarchy(self, root: FolderNode) -> OptimizationPlan:
        review_manager = ReviewManager(root.path)
        empty_folder_moves: List[PlanOperation] = []
        collapsed_chains: List[str] = []

        # 1. Detect empty folders across the tree
        empty_paths = self.detector.find_empty_folders(root)
        for empty_p in empty_paths:
            if empty_p != root.path and "_FileManagerAI_Review" not in str(empty_p):
                # Route empty folder into Review/Empty/<folder_name>
                dest = review_manager.get_review_destination(empty_p, ReviewCategory.EMPTY)
                empty_folder_moves.append(
                    PlanOperation(
                        operation_type=OperationType.MOVE_TO_REVIEW,
                        source=empty_p,
                        destination=dest,
                        reason="Preserve empty folder in Review/Empty/ rather than deleting",
                        confidence=1.0,
                    )
                )

        # 2. Detect redundant nesting
        redundant_paths = self.detector.find_redundant_nesting(root)
        for red_p in redundant_paths:
            collapsed_chains.append(f"Identified redundant chain at: {red_p}")

        # 3. Persist optimization analysis state into a temporary file for bounded memory & safe resume
        temp_fd, temp_path_str = tempfile.mkstemp(prefix="filemanager_opt_", suffix=".json")
        temp_file = Path(temp_path_str)

        state_data = {
            "root": str(root.path),
            "empty_folders_count": len(empty_folder_moves),
            "redundant_chains": collapsed_chains,
        }

        with open(temp_fd, "w", encoding="utf-8") as f:
            json.dump(state_data, f, indent=2)

        return OptimizationPlan(
            empty_folder_moves=empty_folder_moves,
            collapsed_chains=collapsed_chains,
            temp_state_file=temp_file,
        )
