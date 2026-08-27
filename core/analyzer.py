from pathlib import Path

from models.folder_node import FolderNode
from core.tree_builder import TreeBuilder
from core.statistics import FolderStatistics
from core.detector import StructureDetector
from core.health import FolderHealth
from core.report import ReportGenerator, AnalysisSummary


class FolderAnalyzer:
    """Orchestrates full Phase 1 analysis over a folder tree."""

    def __init__(
        self,
        tree_builder: TreeBuilder = None,
        statistics: FolderStatistics = None,
        detector: StructureDetector = None,
        health: FolderHealth = None,
        report_generator: ReportGenerator = None,
    ):
        self.tree_builder = tree_builder or TreeBuilder()
        self.statistics = statistics or FolderStatistics()
        self.detector = detector or StructureDetector()
        self.health = health or FolderHealth(self.detector)
        self.report_generator = report_generator or ReportGenerator()

    def analyze(self, root: FolderNode) -> AnalysisSummary:
        """Runs validation, metrics calculation, structural detection, and health scoring."""
        # 1. Validate tree hierarchy integrity
        validated_root = self.tree_builder.build(root)

        # 2. Compute statistics
        scan_result = self.statistics.calculate(validated_root)

        # 3. Detect structural issues & characteristics
        empty_folders = self.detector.find_empty_folders(validated_root)
        redundant_folders = self.detector.find_redundant_nesting(validated_root)
        deep_folders = self.detector.find_deep_folders(validated_root)
        project_folders = self.detector.find_project_folders(validated_root)

        # 4. Compute overall health score
        health_score = self.health.evaluate(validated_root)

        return AnalysisSummary(
            scan_result=scan_result,
            health_score=health_score,
            empty_folders=empty_folders,
            redundant_folders=redundant_folders,
            deep_folders=deep_folders,
            project_folders=project_folders,
        )

    def generate_report(self, summary: AnalysisSummary) -> str:
        """Produces formatted report text."""
        return self.report_generator.generate_text_report(summary)

    def save_report(self, summary: AnalysisSummary, output_path: Path) -> Path:
        """Saves report text to disk."""
        return self.report_generator.save_report(summary, output_path)
