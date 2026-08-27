from dataclasses import dataclass
from typing import List
from pathlib import Path

from models.scan_result import ScanResult
from core.health import HealthScore


@dataclass
class AnalysisSummary:
    scan_result: ScanResult
    health_score: HealthScore
    empty_folders: List[Path]
    redundant_folders: List[Path]
    deep_folders: List[Path]
    project_folders: List[Path]


class ReportGenerator:
    """Generates human-readable text and markdown reports for folder analysis."""

    def generate_text_report(self, summary: AnalysisSummary) -> str:
        """Generates a plain-text summary of the analysis."""
        lines = [
            "========================================",
            "        FILEMANAGER AI - REPORT         ",
            "========================================",
            f"Root Path: {summary.scan_result.root.path}",
            f"Total Files: {summary.scan_result.total_files}",
            f"Total Folders: {summary.scan_result.total_folders}",
            f"Total Size: {summary.scan_result.total_size} bytes",
            f"Health Score: {summary.health_score.score}/100",
            "----------------------------------------",
        ]

        if summary.health_score.issues_found:
            lines.append("Issues Identified:")
            for issue in summary.health_score.issues_found:
                lines.append(f" - {issue}")
            lines.append("----------------------------------------")

        if summary.project_folders:
            lines.append("Detected Project Directories:")
            for proj in summary.project_folders:
                lines.append(f" - {proj.name}")
            lines.append("----------------------------------------")

        lines.append("========================================")
        return "\n".join(lines)

    def save_report(self, summary: AnalysisSummary, output_path: Path) -> Path:
        """Writes the generated report string to a file."""
        report_text = self.generate_text_report(summary)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report_text, encoding="utf-8")
        return output_path
