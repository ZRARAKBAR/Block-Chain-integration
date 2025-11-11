import tempfile
from src.file_manager import compute_file_hash

def test_hash_small_file():
    with tempfile.NamedTemporaryFile("wb", delete=False) as f:
        f.write(b"hello world")
        path = f.name
    h = compute_file_hash(path)
    assert len(h) == 64
