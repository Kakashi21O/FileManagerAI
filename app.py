from pathlib import Path

from core.config_loader import load_config
from core.scanner import FileScanner


config = load_config(Path("config/settings.yaml"))

scanner = FileScanner(config)

root = scanner.scan(Path("models"))

print(root)