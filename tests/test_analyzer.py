from pathlib import Path
from core.scanner import FileScanner
from core.analyzer import FolderAnalyzer


def test_folder_analyzer_end_to_end(tmp_path):
    # Root with a project folder and an empty folder
    proj_dir = tmp_path / "my_project"
    proj_dir.mkdir()
    (proj_dir / "pyproject.toml").touch()
    (proj_dir / "main.py").write_text("print('hello')")

    empty_dir = tmp_path / "empty_dir"
    empty_dir.mkdir()

    scanner = FileScanner({})
    root = scanner.scan(tmp_path)

    analyzer = FolderAnalyzer()
    summary = analyzer.analyze(root)

    # Validate analysis results
    assert summary.scan_result.total_folders == 3  # root + proj_dir + empty_dir
    assert summary.scan_result.total_files == 2
    assert empty_dir in summary.empty_folders
    assert proj_dir in summary.project_folders

    # Validate report generation through analyzer
    report_text = analyzer.generate_report(summary)
    assert "FILEMANAGER AI - REPORT" in report_text
    assert "my_project" in report_text

    # Validate saving report to file
    out_file = tmp_path / "reports" / "analysis_report.txt"
    saved = analyzer.save_report(summary, out_file)
    assert saved.exists()
