import hashlib
import time
from dataclasses import dataclass, asdict
from storage import save_chain_atomic, load_chain  # <-- import storage functions

@dataclass
class Block:
    index: int
    timestamp: str
    file_name: str
    file_hash: str
    previous_hash: str
    hash: str

    @staticmethod
    def calculate_hash(index, timestamp, file_name, file_hash, previous_hash):
        data = f"{index}|{timestamp}|{file_name}|{file_hash}|{previous_hash}"
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    @classmethod
    def create(cls, index, timestamp, file_name, file_hash, previous_hash):
        h = cls.calculate_hash(index, timestamp, file_name, file_hash, previous_hash)
        return cls(index=index, timestamp=timestamp, file_name=file_name,
                   file_hash=file_hash, previous_hash=previous_hash, hash=h)

class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        genesis = Block.create(0, ts, "Genesis", "0", "0")
        self.chain = [genesis]

    def get_latest(self):
        return self.chain[-1]

    def add_block(self, file_name, file_hash):
        idx = len(self.chain)
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        prev_hash = self.get_latest().hash
        block = Block.create(idx, ts, file_name, file_hash, prev_hash)
        self.chain.append(block)
        return block

    def is_valid(self):
        for i in range(1, len(self.chain)):
            cur = self.chain[i]
            prev = self.chain[i-1]
            recalculated = Block.calculate_hash(cur.index, cur.timestamp, cur.file_name, cur.file_hash, cur.previous_hash)
            if cur.hash != recalculated:
                return False, f"Block {i} hash mismatch (stored {cur.hash} != recalculated {recalculated})"
            if cur.previous_hash != prev.hash:
                return False, f"Block {i} previous_hash mismatch (stored {cur.previous_hash} != prev.hash {prev.hash})"
        return True, "Chain is valid"

    def to_list(self):
        return [asdict(b) for b in self.chain]

    def load_from_list(self, arr):
        self.chain = []
        for b in arr:
            block = Block(b['index'], b['timestamp'], b['file_name'], b['file_hash'], b['previous_hash'], b['hash'])
            self.chain.append(block)

    # --- New methods for GUI ---
    def save_to_file(self, path):
        """
        Saves chain to JSON file using atomic save
        """
        save_chain_atomic(path, self.to_list())

    def load_from_file(self, path):
        """
        Loads chain from JSON file
        """
        arr = load_chain(path)
        self.load_from_list(arr)
