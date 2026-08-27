from pathlib import Path
from core.scanner import FileScanner
from core.optimizer import HierarchyOptimizer


def test_hierarchy_optimizer_routes_empty_folders_to_review(tmp_path):
    # Setup empty folder
    empty_dir = tmp_path / "unused_folder"
    empty_dir.mkdir()

    # Setup non-empty folder
    active_dir = tmp_path / "active_folder"
    active_dir.mkdir()
    (active_dir / "file.txt").touch()

    scanner = FileScanner({})
    root = scanner.scan(tmp_path)

    optimizer = HierarchyOptimizer()
    plan = optimizer.optimize_hierarchy(root)

    assert len(plan.empty_folder_moves) == 1
    assert plan.empty_folder_moves[0].source == empty_dir
    assert "_FileManagerAI_Review" in str(plan.empty_folder_moves[0].destination)
    assert "Empty" in str(plan.empty_folder_moves[0].destination)

    # Verify temp state file was written and exists
    assert plan.temp_state_file.exists()
    # Clean up temp file
    plan.temp_state_file.unlink()
