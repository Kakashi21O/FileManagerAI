import json
import logging
from pathlib import Path
import shutil
from typing import List

logger = logging.getLogger(__name__)


class RollbackEngine:
    """
    Reads transaction records and reverses file operations safely.
    Restores files from destination back to their original source locations.
    """

    def __init__(self, log_path: Path):
        self.log_path = log_path

    def rollback_latest_session(self) -> int:
        """
        Reverses all successful operations recorded in the transaction log in reverse order.
        Returns the count of successfully restored files.
        """
        if not self.log_path.exists():
            logger.warning(f"No transaction log found at {self.log_path}")
            return 0

        records = []
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        records.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        continue

        restored_count = 0

        # Rollback in reverse chronological order
        for rec in reversed(records):
            if rec.get("status") == "SUCCESS":
                src = Path(rec["source"])
                dest = Path(rec["destination"])

                if dest.exists():
                    try:
                        src.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(dest), str(src))
                        restored_count += 1
                        logger.info(f"Restored: {dest} -> {src}")
                    except Exception as e:
                        logger.error(f"Failed to restore {dest} to {src}: {e}")

        return restored_count
