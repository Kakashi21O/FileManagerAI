from pathlib import Path
from models.folder_node import FolderNode
from models.scan_result import ScanResult
from core.health import HealthScore
from core.report import ReportGenerator, AnalysisSummary


def test_generate_text_report():
    root = FolderNode(name="my_folder", path=Path("my_folder"), depth=0)
    scan_result = ScanResult(
        root=root,
        total_files=5,
        total_folders=2,
        total_size=1024
    )
    health = HealthScore(score=85, issues_found=["Found 1 empty folder(s)."])
    summary = AnalysisSummary(
        scan_result=scan_result,
        health_score=health,
        empty_folders=[Path("my_folder/empty")],
        redundant_folders=[],
        deep_folders=[],
        project_folders=[Path("my_folder/project")]
    )

    generator = ReportGenerator()
    report_text = generator.generate_text_report(summary)

    assert "FILEMANAGER AI - REPORT" in report_text
    assert "Total Files: 5" in report_text
    assert "Total Folders: 2" in report_text
    assert "Health Score: 85/100" in report_text
    assert "Found 1 empty folder(s)." in report_text
    assert "project" in report_text


def test_save_report(tmp_path):
    root = FolderNode(name="test", path=tmp_path, depth=0)
    scan_result = ScanResult(root=root, total_files=0, total_folders=1, total_size=0)
    health = HealthScore(score=100, issues_found=[])
    summary = AnalysisSummary(
        scan_result=scan_result,
        health_score=health,
        empty_folders=[],
        redundant_folders=[],
        deep_folders=[],
        project_folders=[]
    )

    generator = ReportGenerator()
    output_file = tmp_path / "reports" / "summary.txt"
    saved_path = generator.save_report(summary, output_file)

    assert saved_path.exists()
    assert "FILEMANAGER AI - REPORT" in saved_path.read_text(encoding="utf-8")
