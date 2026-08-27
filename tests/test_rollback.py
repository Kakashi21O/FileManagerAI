from pathlib import Path
from core.executor import ExecutionEngine
from core.planner import PlanOperation, OperationType
from core.rollback import RollbackEngine
from core.transaction import TransactionLogger


def test_rollback_engine_reverses_moves(tmp_path):
    src = tmp_path / "original_script.py"
    src.write_text("print('hello rollback')")

    dest = tmp_path / "Code" / "original_script.py"

    log_file = tmp_path / "logs" / "transactions.jsonl"
    logger = TransactionLogger(log_file)

    op = PlanOperation(
        operation_type=OperationType.MOVE,
        source=src,
        destination=dest,
        reason="Test",
    )

    # 1. Execute move with apply
    engine = ExecutionEngine(transaction_logger=logger)
    engine.execute([op], dry_run=False)

    assert not src.exists()
    assert dest.exists()

    # 2. Run Rollback
    rollback = RollbackEngine(log_file)
    restored = rollback.rollback_latest_session()

    assert restored == 1
    assert src.exists()
    assert not dest.exists()
    assert src.read_text() == "print('hello rollback')"
