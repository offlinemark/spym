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
        # conscientiously /not/ checking if they're overwriting data section
        # memory because that's their fault, and not our responsibility
        if addr < 0 or addr + len(buffer) > self.size():
            raise Exception('write outside memory bounds')
        elif len(buffer) == 0:
            raise Exception('empty buffer to write')
        self.memory[addr:addr+len(buffer)] = buffer

    def size(self):
        return len(self.memory)

    def dump(self):
        fmt = '{:04x}: {}{} {}{}  {} {}'

        for i in range(0, self.size(), 8):
            word = self.memory[i:i+4] if i <= self.size() - 4 else self.memory[i:]
            word2 = self.memory[i+4:i+8] if i <= self.size() - 8 else self.memory[i+4:]

            print fmt.format(i, binascii.hexlify(word), self._pad(word),
                             binascii.hexlify(word2), self._pad(word2),
                             self._print_version(word),
                             self._print_version(word2))

    def _pad(self, str):
        # str is the 4 byte string, occupying 8 characters when hexlified.
        return ' ' * (8-len(str)*2)

    def _print_version(self, word):
        ret = ''
        for char in word:
            ret += chr(char) if char > 0x20 and char < 0x7f else '.'
        return ret
