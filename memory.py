class Memory(object):
    def __init__(self, mem):
        self.memory = bytearray([0] * mem)

    def read(self, addr, count):
        return str(self.memory[addr:addr+count])

    def write(self, addr, buffer):
        self.memory[addr:addr+len(buffer)] = buffer

    def dump(self):
        print repr(self.memory)
