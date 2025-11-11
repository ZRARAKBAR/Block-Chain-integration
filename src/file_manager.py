import hashlib
import os

def compute_file_hash(file_path, progress_callback=None, chunk_size=65536):
    """
    Compute SHA-256 of file using chunks. Optionally call progress_callback(read, total)
    """
    sha256 = hashlib.sha256()
    total = os.path.getsize(file_path)
    read = 0
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            sha256.update(chunk)
            read += len(chunk)
            if progress_callback:
                progress_callback(read, total)
    return sha256.hexdigest()
