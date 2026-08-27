from dataclasses import asdict, dataclass
import json
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


@dataclass
class TransactionRecord:
    timestamp: str
    operation: str
    source: str
    destination: str
    reason: str
    status: str


class TransactionLogger:
    """
    Maintains an append-only JSONL log of every file movement
    to provide auditability and future rollback capability.
    """

    def __init__(self, log_path: Path):
        self.log_path = log_path

    def record(self, record: TransactionRecord) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(record)) + "\n")
        except OSError as e:
            logger.error(f"Failed to record transaction log: {e}")
