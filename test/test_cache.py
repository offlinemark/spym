from emu.cache import Cache, CacheAddr
from emu.memory import Memory


def addr2block(cache, addr):
    return cache.cache[CacheAddr(addr).index]


def test_read():
    m = Memory(64)
    m.write(0, 'aaaabbbbccccdddd')
    c = Cache(m)

    # cache miss, aligned
    assert c.read(0) == 'aaaa'
    b = addr2block(c, 0)
    assert b.dirty == False
    assert b.valid == True
    assert b.data == 'aaaabbbb'

    # cache miss, unaligned
    assert c.read(9) == 'cccd'
    b = addr2block(c, 9)
    assert b.dirty == False
    assert b.valid == True
    assert b.data == 'ccccdddd'

    # cache hit, aligned
    assert c.read(4) == 'bbbb'
    b = addr2block(c, 4)
    assert b.valid == True
    assert b.data == 'aaaabbbb'

    # cache hit, unaligned
    assert c.read(1) == 'aaab'


def test_write():
    m = Memory(64)
    c = Cache(m)

    # cache miss, aligned
    c.write(0, 'yoyo')
    assert c.read(0) == 'yoyo'
    b = addr2block(c, 0)
    assert b.dirty == False
    assert b.valid == True
    assert b.tag == 0
    assert b.data == 'yoyo\x00\x00\x00\x00'

    # cache miss, unaligned
    c.write(9, 'yoyo')
    assert c.read(9) == 'yoyo'
    b = addr2block(c, 9)
    assert b.dirty == False
    assert b.valid == True
    assert b.tag == 0
    assert b.data == '\x00yoyo\x00\x00\x00'

    # cache hit, aligned
    c.write(0, 'yoya')
    assert c.read(0) == 'yoya'
    b = addr2block(c, 0)
    assert b.dirty == True
    assert b.valid == True
    assert b.tag == 0
    assert b.data == 'yoya\x00\x00\x00\x00'

    # cache hit, unaligned
    c.write(9, 'yoya')
    assert c.read(9) == 'yoya'
    b = addr2block(c, 9)
    assert b.dirty == True
    assert b.valid == True
    assert b.tag == 0
    assert b.data == '\x00yoya\x00\x00\x00'

def test_straddle():
    m = Memory(64)
    m.write(0, 'aaaabbbbccccdddd')
    c = Cache(m)
    # straddle 0 and 1 blocks
    assert c.read(5) == 'bbbc'
