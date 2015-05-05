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
        fmt = '{:04x}  {}{} {}{}  {} {}'

        # we are processing memory from the end of the bytearray to the front
        # so our output can visually go from high memory (end of bytearray)
        # at the top, to low memory (beginning of bytearray) at the bottom
        for i in range(self.size()-1, -1, -8):

            # whew, ok. for any index >= 4, word is really happy and just
            # scoops up the next 4 bytes. otherwise we've landed really
            # close to the end of memory and don't even have 4 bytes left,
            # so we just scooop up whatever's there
            word = self.memory[i:i-4:-1] if i >= 4 else self.memory[i::-1]

            # word2 is a little more complex. for any index >= 8, we can scoop
            # up the second word with this little i-8 thing. note that this
            # does /not/ work for i=7, even though there are still 8 bytes
            # left. for any index >= 5, that means there aren't 4 bytes left
            # in word2, but there are /some/ bytes, so we scoop them up.
            # lastly, if there are less than 5 bytes, then all the remaining
            # bytes will be claimed by word and there are none for word2
            word2 = self.memory[i-4:i-8:-1] if i >= 8 else self.memory[i-4::-1] if i >= 5 else ''

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
