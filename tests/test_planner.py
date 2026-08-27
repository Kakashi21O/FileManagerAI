from pathlib import Path
from core.scanner import FileScanner
from core.planner import OrganizationPlanner, OperationType


def test_planner_organizes_loose_files(tmp_path):
    # Loose files
    (tmp_path / "script.py").touch()
    (tmp_path / "photo.png").touch()

    scanner = FileScanner({})
    root = scanner.scan(tmp_path)

    planner = OrganizationPlanner()
    plan = planner.create_plan(root)

    assert len(plan.operations) == 2
    sources = {op.source.name for op in plan.operations}
    assert sources == {"script.py", "photo.png"}


def test_planner_protects_project_folders(tmp_path):
    # Setup project folder
    proj = tmp_path / "my_app"
    proj.mkdir()
    (proj / "pyproject.toml").touch()
    (proj / "main.py").touch()

    scanner = FileScanner({})
    root = scanner.scan(tmp_path)

    planner = OrganizationPlanner()
    plan = planner.create_plan(root)

    # Project files must not be torn apart
    assert len(plan.operations) == 0


def test_planner_routes_duplicate_to_review(tmp_path):
    # Setup duplicate
    f1 = tmp_path / "doc.txt"
    f1.write_text("Hello duplicate test")

    sub = tmp_path / "sub"
    sub.mkdir()
    f2 = sub / "doc_copy.txt"
    f2.write_text("Hello duplicate test")

    scanner = FileScanner({})
    root = scanner.scan(tmp_path)

    planner = OrganizationPlanner()
    plan = planner.create_plan(root)

    dup_ops = [op for op in plan.operations if op.operation_type == OperationType.MOVE_TO_REVIEW]
    assert len(dup_ops) == 1
    assert dup_ops[0].source == f2
    assert "_FileManagerAI_Review" in str(dup_ops[0].destination)
