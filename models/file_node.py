from dataclasses import dataclass
from pathlib import Path


@dataclass
class FileNode:
    name: str
    path: Path
    extension: str
    size: int
    depth: int