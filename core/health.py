from dataclasses import dataclass, field
from typing import List
from pathlib import Path
from models.folder_node import FolderNode
from core.detector import StructureDetector


@dataclass
class HealthScore:
    score: int  # 0 to 100
    issues_found: List[str] = field(default_factory=list)


class FolderHealth:
    """Evaluates directory structure health and cleanliness score."""

    def __init__(self, detector: StructureDetector = None):
        self.detector = detector or StructureDetector()

    def evaluate(self, root: FolderNode) -> HealthScore:
        issues: List[str] = []
        score = 100

        empty_folders = self.detector.find_empty_folders(root)
        redundant_folders = self.detector.find_redundant_nesting(root)
        deep_folders = self.detector.find_deep_folders(root)

        if empty_folders:
            issues.append(f"Found {len(empty_folders)} empty folder(s).")
            # Deduct 5 points per empty folder, maximum deduction 25
            score -= min(25, len(empty_folders) * 5)

        if redundant_folders:
            issues.append(f"Found {len(redundant_folders)} redundantly nested folder(s).")
            # Deduct 10 points per redundant chain, maximum deduction 30
            score -= min(30, len(redundant_folders) * 10)

        if deep_folders:
            issues.append(f"Found {len(deep_folders)} folder(s) exceeding max recommended depth.")
            # Deduct 10 points per deeply nested folder, maximum deduction 30
            score -= min(30, len(deep_folders) * 10)

        # Score stays within 0 to 100
        score = max(0, min(100, score))

        return HealthScore(score=score, issues_found=issues)
