from emu.cache import Cache
from emu.memory import Memory


def test_hit():
    m = Memory(64)
    m.write(0, 'aaaabbbbccccdddd')
    c = Cache(m)
    # cache miss, aligned
    assert c.read(0) == 'aaaa'
    # cache miss, unaligned
    assert c.read(9) == 'cccd'
    # cache hit, aligned
    assert c.read(4) == 'bbbb'
    # cache hit, unaligned
    assert c.read(1) == 'aaab'

def test_straddle():
    m = Memory(64)
    m.write(0, 'aaaabbbbccccdddd')
    c = Cache(m)
    # straddle 0 and 1 blocks
    assert c.read(5) == 'bbbc'

def test_write():
    m = Memory(64)
    c = Cache(m)
    c.write(0, 'yoyo')
