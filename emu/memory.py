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
        print repr(self.memory)
