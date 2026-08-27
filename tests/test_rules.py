from pathlib import Path
from core.rules import CategoryClassifier, FileCategory


def test_category_classifier():
    classifier = CategoryClassifier()

    assert classifier.classify(Path("app.py")) == FileCategory.CODE
    assert classifier.classify(Path("script.ts")) == FileCategory.CODE
    assert classifier.classify(Path("photo.PNG")) == FileCategory.IMAGE
    assert classifier.classify(Path("logo.webp")) == FileCategory.IMAGE
    assert classifier.classify(Path("notes.txt")) == FileCategory.DOCUMENT
    assert classifier.classify(Path("config.yaml")) == FileCategory.DATA
    assert classifier.classify(Path("backup.tar.gz")) == FileCategory.ARCHIVE
    assert classifier.classify(Path("unknown.xyz123")) == FileCategory.OTHER
