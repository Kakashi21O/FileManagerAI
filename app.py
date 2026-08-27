from pathlib import Path

from core.config_loader import load_config
from core.scanner import FileScanner
from core.analyzer import FolderAnalyzer


def main():
    # Load configuration
    config_path = Path("config/settings.yaml")
    config = load_config(config_path) if config_path.exists() else {}

    # Scan directory
    target_path = Path("models")
    scanner = FileScanner(config)
    root = scanner.scan(target_path)

    # Perform full analysis
    analyzer = FolderAnalyzer()
    summary = analyzer.analyze(root)

    # Print summary report to console
    report_text = analyzer.generate_report(summary)
    print(report_text)


if __name__ == "__main__":
    main()