import pytest
from src.blockchain import Blockchain

def test_genesis_and_add():
    bc = Blockchain()
    assert len(bc.chain) == 1
    b = bc.add_block("file.txt", "abc")
    assert len(bc.chain) == 2
    ok,msg = bc.is_valid()
    assert ok
