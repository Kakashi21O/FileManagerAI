from pathlib import Path
from core.executor import ExecutionEngine
from core.planner import PlanOperation, OperationType
from core.transaction import TransactionLogger


def test_executor_dry_run_does_not_move_files(tmp_path):
    src = tmp_path / "loose_script.py"
    src.write_text("print('safe')")

    dest = tmp_path / "Code" / "loose_script.py"

    op = PlanOperation(
        operation_type=OperationType.MOVE,
        source=src,
        destination=dest,
        reason="Test dry run",
    )

    engine = ExecutionEngine()
    records = engine.execute([op], dry_run=True)

    assert len(records) == 1
    assert records[0].status == "SIMULATED"
    # Source file MUST still be at original location
    assert src.exists()
    assert not dest.exists()


def test_executor_apply_mode_moves_file_and_logs(tmp_path):
    src = tmp_path / "loose_photo.png"
    src.write_text("fake image bytes")

    dest = tmp_path / "Images" / "loose_photo.png"

    log_file = tmp_path / "logs" / "test_txn.jsonl"
    logger = TransactionLogger(log_file)

    op = PlanOperation(
        operation_type=OperationType.MOVE,
        source=src,
        destination=dest,
        reason="Test apply mode",
    )

    engine = ExecutionEngine(transaction_logger=logger)
    records = engine.execute([op], dry_run=False)

    assert len(records) == 1
    assert records[0].status == "SUCCESS"
    assert not src.exists()
    assert dest.exists()
    assert log_file.exists()
    assert "loose_photo.png" in log_file.read_text(encoding="utf-8")
