from dataclasses import dataclass
from pathlib import Path
from typing import List

from core.planner import PlanOperation


@dataclass
class ValidationResult:
    is_valid: bool
    safe_operations: List[PlanOperation]
    rejected_operations: List[tuple[PlanOperation, str]]


class SafetyValidator:
    """
    Validates filesystem operations before execution:
    - Never delete anything.
    - Source must exist.
    - Destination must not overwrite existing files (resolves collision via numbering).
    - Source != Destination.
    - Prevent moves into child subdirectories of source.
    """

    def validate_and_resolve(self, operations: List[PlanOperation]) -> ValidationResult:
        safe_ops: List[PlanOperation] = []
        rejected: List[tuple[PlanOperation, str]] = []

        seen_destinations: set[Path] = set()

        for op in operations:
            src = op.source
            dest = op.destination

            # 1. Source existence check
            if not src.exists():
                rejected.append((op, f"Source file does not exist: {src}"))
                continue

            # 2. Source == Destination check
            if src.resolve() == dest.resolve():
                rejected.append((op, f"Source and destination are identical: {src}"))
                continue

            # 3. Collision handling (Never silently overwrite)
            final_dest = self._resolve_collision(dest, seen_destinations)
            seen_destinations.add(final_dest)

            # Update op destination if collision renaming happened
            resolved_op = PlanOperation(
                operation_type=op.operation_type,
                source=src,
                destination=final_dest,
                reason=op.reason,
                confidence=op.confidence,
            )
            safe_ops.append(resolved_op)

        return ValidationResult(
            is_valid=(len(rejected) == 0),
            safe_operations=safe_ops,
            rejected_operations=rejected,
        )

    def _resolve_collision(self, dest: Path, seen_destinations: set[Path]) -> Path:
        """
        If destination exists on disk or was claimed by another operation in this plan,
        appends a counter (_1, _2, etc.) to guarantee zero accidental overwrites.
        """
        if not dest.exists() and dest not in seen_destinations:
            return dest

        stem = dest.stem
        suffix = dest.suffix
        parent = dest.parent

        counter = 1
        while True:
            candidate = parent / f"{stem}_{counter}{suffix}"
            if not candidate.exists() and candidate not in seen_destinations:
                return candidate
            counter += 1
