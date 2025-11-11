import json
import os
import tempfile

def save_chain_atomic(path, chain_list):
    """
    Save JSON atomically: write to tmp then rename.
    """
    dirn = os.path.dirname(path)
    os.makedirs(dirn, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=dirn, prefix="chain_", suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(chain_list, f, indent=2)
    os.replace(tmp_path, path)

def load_chain(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
