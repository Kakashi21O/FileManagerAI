from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class FolderNode:
    name: str
    path: Path
    depth: int
    files: list = field(default_factory=list)
    children: list = field(default_factory=list)