from pathlib import Path

from core.path_utils import (
    get_name,
    get_extension,
    get_parent,
    get_absolute_path,
    is_file,
    is_folder,
)


def test_get_name():
    path = Path("test_file.py")

    result = get_name(path)

    assert result == "test_file.py"


def test_get_extension():
    path = Path("test_file.py")

    result = get_extension(path)

    assert result == ".py"


def test_get_parent():
    path = Path("Project/test_file.py")

    result = get_parent(path)

    assert result == Path("Project")


def test_get_absolute_path():
    path = Path("test_file.py")

    result = get_absolute_path(path)

    assert result.is_absolute()


def test_is_file(tmp_path):
    file = tmp_path / "test.txt"
    file.touch()

    assert is_file(file) is True


def test_is_folder(tmp_path):
    folder = tmp_path / "test_folder"
    folder.mkdir()

    assert is_folder(folder) is True