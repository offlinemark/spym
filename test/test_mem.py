import struct
import pytest

from emu.memory import Memory

mem = Memory(16)
mem.memory = bytearray(struct.pack('<IIII', 1, 2, 3, 4))


def test_read():
    assert mem.read(0, 4) == struct.pack('<I', 1)
    assert mem.read(4, 4) == struct.pack('<I', 2)


def test_bad_read():
    with pytest.raises(Exception):
        mem.read(13, 4) == struct.pack('<I', 4)
    with pytest.raises(Exception):
        mem.read(-1, 4) == struct.pack('<I', 4)
    with pytest.raises(Exception):
        mem.read(2, 33) == struct.pack('<I', 4)
    with pytest.raises(Exception):
        mem.read(0, -4) == struct.pack('<I', 4)


def test_write():
    mem.write(0, struct.pack('<I', 9))
    assert mem.read(0, 4) == struct.pack('<I', 9)
    mem.write(12, struct.pack('<I', 9))
    assert mem.read(12, 4) == struct.pack('<I', 9)
    mem.write(1, struct.pack('<I', 9))
    assert mem.read(1, 4) == struct.pack('<I', 9)


def test_bad_write():
    with pytest.raises(Exception):
        mem.write(-1, 'yoyo')
    with pytest.raises(Exception):
        mem.write(13, 'yoyo')
    with pytest.raises(Exception):
        mem.write(0, '')
