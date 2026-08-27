from pathlib import Path
from core.planner import PlanOperation, OperationType
from core.safety import SafetyValidator


def test_safety_validator_resolves_collision(tmp_path):
    src = tmp_path / "photo.png"
    src.touch()

    # Create collision at destination
    dest = tmp_path / "Images" / "photo.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.touch()

    op = PlanOperation(
        operation_type=OperationType.MOVE,
        source=src,
        destination=dest,
        reason="Categorize image",
    )

    validator = SafetyValidator()
    result = validator.validate_and_resolve([op])

    assert result.is_valid is True
    assert len(result.safe_operations) == 1
    assert result.safe_operations[0].destination.name == "photo_1.png"


def test_safety_validator_rejects_missing_source(tmp_path):
    missing_src = tmp_path / "missing.txt"
    dest = tmp_path / "Documents" / "missing.txt"

    op = PlanOperation(
        operation_type=OperationType.MOVE,
        source=missing_src,
        destination=dest,
        reason="Categorize",
    )

    validator = SafetyValidator()
    result = validator.validate_and_resolve([op])

    assert result.is_valid is False
    assert len(result.rejected_operations) == 1
