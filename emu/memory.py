from util.hexdump import hexdump


class Memory(object):
    """Generic memory abstaction."""

    def __init__(self, size):
        self.memory = bytearray([0] * size)

    def read(self, addr, count):
        import time
        print 'hit memory'
        time.sleep(1)
        if addr < 0 or addr + count > self.size():
            raise Exception('read outside memory bounds')
        elif count < 0:
            raise Exception('negative memory read')
        return self.memory[addr:addr+count]

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
        hexdump(self.memory, True)
