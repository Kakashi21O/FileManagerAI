import argparse
import logging
from pathlib import Path

from core.analyzer import FolderAnalyzer
from core.config_loader import load_config
from core.executor import ExecutionEngine
from core.planner import OrganizationPlanner
from core.scanner import FileScanner

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("FileManagerAI")


def main():
    parser = argparse.ArgumentParser(description="FileManagerAI - Safe & Intelligent Filesystem Organizer")
    parser.add_argument("--path", type=str, default="models", help="Directory path to scan and organize")
    parser.add_argument("--apply", action="store_true", help="Apply organization plan changes to disk (Default is dry-run)")
    args = parser.parse_args()

    # Load configuration
    config_path = Path("config/settings.yaml")
    config = load_config(config_path) if config_path.exists() else {}

    target_path = Path(args.path)
    logger.info(f"Scanning target directory: {target_path}")

    # 1. Scan filesystem
    scanner = FileScanner(config)
    root = scanner.scan(target_path)

    # 2. Structural Analysis
    analyzer = FolderAnalyzer()
    summary = analyzer.analyze(root)
    print(analyzer.generate_report(summary))

    # 3. Organization Planning
    planner = OrganizationPlanner()
    plan = planner.create_plan(root)

    print(f"\nOrganization Plan: {len(plan.operations)} operations generated.")
    for op in plan.operations:
        print(f"[{op.operation_type}] {op.source.name} -> {op.destination.relative_to(target_path) if target_path in op.destination.parents else op.destination} ({op.reason})")

    # 4. Execution (Dry-Run by default, Apply when requested)
    is_dry_run = not args.apply
    if is_dry_run:
        print("\nMode: DRY RUN (Simulated only, no files modified. Use --apply to execute).")
    else:
        print("\nMode: APPLY (Executing operations with absolute safety rules).")

    engine = ExecutionEngine()
    records = engine.execute(plan.operations, dry_run=is_dry_run)
    print(f"Completed {len(records)} operation(s).")


if __name__ == "__main__":
    main()
