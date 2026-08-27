from pathlib import Path
from core.scanner import FileScanner
from core.detector import StructureDetector
from core.context_engine import ContextEngine


def test_context_engine_recognizes_content_keywords(tmp_path):
    ai_script = tmp_path / "model.py"
    ai_script.write_text("import torch\nimport torch.nn as nn\nclass Net(nn.Module): pass")

    scanner = FileScanner({})
    root = scanner.scan(tmp_path)
    file_node = root.files[0]

    engine = ContextEngine()
    context = engine.analyze_context(file_node, root, set())

    assert context.detected_topic == "AI/ML"
    assert context.confidence >= 0.85
    assert context.suggested_target_folder == "Python/AI"


def test_context_engine_insufficient_confidence_does_not_guess(tmp_path):
    random_file = tmp_path / "random_notes.dat"
    random_file.write_text("just some random untyped content")

    scanner = FileScanner({})
    root = scanner.scan(tmp_path)
    file_node = root.files[0]

    engine = ContextEngine()
    context = engine.analyze_context(file_node, root, set())

    assert context.confidence < 0.75
    assert context.suggested_target_folder is None
