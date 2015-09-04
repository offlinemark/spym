'''Direct-mapped data memory cache.
'''
# ADDR_BITS = 32
# CACHE_BYTES = 256
# WORD_BYTES = 4
# BLOCK_BYTES = 16

import binascii
import logging as log

ADDR_BITS = 32
WORD_BYTES = 4

# tiny cache c:
CACHE_BYTES = 32
BLOCK_BYTES = 8

num_blocks = CACHE_BYTES / BLOCK_BYTES
index_len = (num_blocks-1).bit_length()
index_mask = num_blocks - 1
offset_len = (BLOCK_BYTES-1).bit_length()
offset_mask = BLOCK_BYTES - 1


class Block(object):
    def __init__(self):
        self.valid = False
        self.tag = 0
        self.data = bytearray([0] * BLOCK_BYTES)


class CacheAddr(object):
    def __init__(self, addr):
        self.raw = addr
        self.offset = addr & offset_mask
        self.index = (addr >> offset_len) & index_mask
        self.tag = addr >> (index_len + offset_len)


class Cache(object):
    def __init__(self, dmem):
        self.cache = [Block() for i in xrange(num_blocks)]
        self.dmem = dmem

    def read(self, addr):
        """Return word at addr, deferring to main mem if necessary."""

        caddr = CacheAddr(addr)
        block = self.cache[caddr.index]
        if block.valid and block.tag == caddr.tag:
            word = block.data[caddr.offset:caddr.offset+WORD_BYTES]
            if len(word) != WORD_BYTES:
                # word was straddling blocks
                try:
                    next_block = self.cache[caddr.index+1]
                    word += next_block.data[:WORD_BYTES-len(ret)]
                    return word
                except IndexError:
                    # fell off the end of cache, cache miss
                    pass
            else:
                print 'hit cache!'
                return word

        # retrieve block from main memory
        word = self.dmem.read(addr, BLOCK_BYTES)

        # write back to cache
        block.valid = True
        block.tag = caddr.tag
        # TODO dmem.read should prob just ret a bytearray
        block.data = bytearray(word)

        return word[:WORD_BYTES]


    def write(self, addr, buffer):
        pass

    def dump(self):
        log.info('block\tvalid\ttag\tdata')
        log.info('-'*40)
        for i, block in enumerate(self.cache):
            log.info('{}\t{}\t{}\t{}'.format(i, block.valid, block.tag, binascii.hexlify(block.data)))
