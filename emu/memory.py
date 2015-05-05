import binascii


class Memory(object):
    """Generic memory abstaction."""

    def __init__(self, size):
        self.memory = bytearray([0] * size)

    def read(self, addr, count):
        if addr < 0 or addr + count > self.size():
            raise Exception('read outside memory bounds')
        elif count < 0:
            raise Exception('negative memory read')
        return str(self.memory[addr:addr+count])

    def write(self, addr, buffer):
        if addr < 0 or addr + len(buffer) > self.size():
            raise Exception('write outside memory bounds')
        elif len(buffer) == 0:
            raise Exception('empty buffer to write')
        self.memory[addr:addr+len(buffer)] = buffer

    def size(self):
        return len(self.memory)

    def dump(self):
        for i in range(self.size() - 1, 0, -8):
            word = self.memory[i:i-4:-1]
            word2 = self.memory[i-4:i-8:-1]
            print '{:04x}  {} {}  {} {}'.format(i, binascii.hexlify(word),
                                                binascii.hexlify(word2),
                                                self._print_version(word),
                                                self._print_version(word2))

    def _print_version(self, word):
        ret = ''
        for char in word:
            ret += chr(char) if char > 0x20 and char < 0x7f  else '.'
        return ret
