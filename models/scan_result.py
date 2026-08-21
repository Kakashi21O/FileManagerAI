from dataclasses import dataclass


@dataclass
class ScanResult:
    root: object
    total_files: int = 0
    total_folders: int = 0
    total_size: int = 0