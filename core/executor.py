from datetime import datetime, timezone
import logging
from pathlib import Path
import shutil
from typing import List, Optional

from core.planner import PlanOperation
from core.safety import SafetyValidator
from core.transaction import TransactionLogger, TransactionRecord

logger = logging.getLogger(__name__)


class ExecutionEngine:
    """
    Executes validated operations safely.
    Strictly forbids DELETE.
    Supports dry-run simulation and writes transactions to log.
    """

    def __init__(
        self,
        validator: Optional[SafetyValidator] = None,
        transaction_logger: Optional[TransactionLogger] = None,
    ):
        self.validator = validator or SafetyValidator()
        self.transaction_logger = transaction_logger or TransactionLogger(
            Path("logs/transactions.jsonl")
        )

    def execute(self, operations: List[PlanOperation], dry_run: bool = True) -> List[TransactionRecord]:
        validation = self.validator.validate_and_resolve(operations)
        records: List[TransactionRecord] = []

        for op in validation.safe_operations:
            now_str = datetime.now(timezone.utc).isoformat()

            if dry_run:
                record = TransactionRecord(
                    timestamp=now_str,
                    operation=f"DRY_RUN_{op.operation_type}",
                    source=str(op.source),
                    destination=str(op.destination),
                    reason=op.reason,
                    status="SIMULATED",
                )
                records.append(record)
                continue

            # Real execution with safety guarantees
            try:
                op.destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(op.source), str(op.destination))
                status = "SUCCESS"
            except Exception as e:
                logger.error(f"Error moving {op.source} to {op.destination}: {e}")
                status = f"FAILED: {e}"

            record = TransactionRecord(
                timestamp=now_str,
                operation=op.operation_type,
                source=str(op.source),
                destination=str(op.destination),
                reason=op.reason,
                status=status,
            )
            self.transaction_logger.record(record)
            records.append(record)

        return records
