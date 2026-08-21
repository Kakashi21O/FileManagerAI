from pathlib import Path


def get_name(path: Path) -> str:
    return path.name


def get_extension(path: Path) -> str:
    return path.suffix


def get_parent(path: Path) -> Path:
    return path.parent


def get_absolute_path(path: Path) -> Path:
    return path.absolute()


def is_file(path: Path) -> bool:
    return path.is_file()


def is_folder(path: Path) -> bool:
    return path.is_dir()