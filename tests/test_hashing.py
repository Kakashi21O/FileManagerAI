import hashlib
from pathlib import Path
from core.hashing import FileHasher


def test_file_hasher_small_file(tmp_path):
    test_file = tmp_path / "sample.txt"
    content = b"Hello, FileManagerAI streaming hasher!"
    test_file.write_bytes(content)

    expected_hash = hashlib.sha256(content).hexdigest()

    hasher = FileHasher(chunk_size_mb=1)
    actual_hash = hasher.compute_sha256(test_file)

    assert actual_hash == expected_hash


def test_file_hasher_multi_chunk(tmp_path):
    # Test streaming across multiple chunks with small chunk size (1 KB buffer)
    test_file = tmp_path / "large_chunk_test.bin"
    content = b"A" * 5000  # 5 KB
    test_file.write_bytes(content)

    expected_hash = hashlib.sha256(content).hexdigest()

    # Instantiate with custom chunk size
    hasher = FileHasher(chunk_size_mb=1)
    hasher.chunk_size = 1024  # Force 1KB chunks for testing multiple iterations

    actual_hash = hasher.compute_sha256(test_file)
    assert actual_hash == expected_hash


def test_file_hasher_nonexistent_file(tmp_path):
    hasher = FileHasher()
    missing_file = tmp_path / "does_not_exist.txt"
    result = hasher.compute_sha256(missing_file)
    assert result is None
