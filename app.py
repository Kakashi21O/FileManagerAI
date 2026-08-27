import argparse
import logging
from pathlib import Path
import sys

from core.analyzer import FolderAnalyzer
from core.config_loader import load_config
from core.executor import ExecutionEngine
from core.planner import OrganizationPlanner, OperationType
from core.rollback import RollbackEngine
from core.scanner import FileScanner
from core.transaction import TransactionLogger

# ANSI Color codes for clean terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BLUE = "\033[94m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def main():
    parser = argparse.ArgumentParser(description="FileManagerAI - Safe & Intelligent Filesystem Organizer")
    parser.add_argument("--path", type=str, default="models", help="Directory path to scan and organize")
    parser.add_argument("--apply", action="store_true", help="Apply organization plan changes to disk (Default is dry-run)")
    parser.add_argument("--rollback", action="store_true", help="Rollback previously applied operations using transaction log")
    parser.add_argument("--no-log", action="store_true", help="Disable logging transactions to disk")
    args = parser.parse_args()

    # Load configuration
    config_path = Path("config/settings.yaml")
    config = load_config(config_path) if config_path.exists() else {}

    # Logging setting (Config + CLI flag)
    logging_enabled = config.get("enable_logging", True) and not args.no_log
    log_file = Path("logs/transactions.jsonl")

    # Handle Rollback if requested
    if args.rollback:
        engine = RollbackEngine(log_file)
        restored = engine.rollback_latest_session()
        print(f"\n{GREEN}{BOLD}[OK] Rollback complete.{RESET} Restored {BOLD}{restored}{RESET} file(s) to original paths.")
        return

    target_path = Path(args.path)
    print(f"\n{CYAN}{BOLD}>>> Target Directory:{RESET} {target_path.resolve()}")
    print(f"{CYAN}{BOLD}>>> Transaction Logging:{RESET} {'ENABLED (' + str(log_file) + ')' if logging_enabled else 'DISABLED'}")

    # 1. Scan filesystem
    scanner = FileScanner(config)
    root = scanner.scan(target_path)

    # 2. Structural Analysis
    analyzer = FolderAnalyzer()
    summary = analyzer.analyze(root)
    print("\n" + analyzer.generate_report(summary))

    # 3. Organization Planning
    planner = OrganizationPlanner()
    plan = planner.create_plan(root)

    print(f"\n{BOLD}================================================================{RESET}")
    print(f"{BOLD}                  ORGANIZATION PLAN PROPOSAL                    {RESET}")
    print(f"{BOLD}================================================================{RESET}")

    if not plan.operations:
        print(f"{GREEN}[OK] Folder structure is already clean and well-organized. No moves needed!{RESET}")
    else:
        print(f"Total Operations Planned: {BOLD}{len(plan.operations)}{RESET}\n")
        for i, op in enumerate(plan.operations, 1):
            tag_color = YELLOW if op.operation_type == OperationType.MOVE_TO_REVIEW else BLUE
            dest_display = op.destination.relative_to(target_path) if target_path in op.destination.parents else op.destination

            print(f" {BOLD}{i:02d}.{RESET} [{tag_color}{op.operation_type}{RESET}]")
            print(f"     {BOLD}Source:{RESET}      {op.source}")
            print(f"     {BOLD}Destination:{RESET} {dest_display}")
            print(f"     {BOLD}Reason:{RESET}      {op.reason}")
            print(f"     {BOLD}Confidence:{RESET}  {op.confidence * 100:.0f}%\n")

    # 4. Execution Engine
    is_dry_run = not args.apply
    if is_dry_run:
        print(f"{YELLOW}{BOLD}>>> MODE: DRY RUN (Preview only -- no files or folders moved on disk){RESET}")
        print(f"  To execute these moves safely, re-run with: {BOLD}python app.py --path \"{target_path}\" --apply{RESET}\n")
    else:
        print(f"{GREEN}{BOLD}>>> MODE: APPLY (Executing operations with absolute safety rules){RESET}\n")

    txn_logger = TransactionLogger(log_file, enabled=logging_enabled)
    engine = ExecutionEngine(transaction_logger=txn_logger)
    records = engine.execute(plan.operations, dry_run=is_dry_run)

    for rec in records:
        status_color = GREEN if rec.status in ("SUCCESS", "SIMULATED") else RED
        print(f" * [{status_color}{rec.status}{RESET}] {Path(rec.source).name} -> {rec.destination}")

    print(f"\n{BOLD}Completed {len(records)} operation(s).{RESET}\n")


if __name__ == "__main__":
    main()


