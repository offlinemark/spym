import sys
import re
import struct

from registers import Registers
from memory import Memory


class CPU(object):
    def __init__(self, mem):
        self.r = Registers()
        self.m = Memory(mem)

    def execute(self, line):
        instr = line.split()
        opcode = instr[0]
        if opcode == 'li':
            # li rd, imm
            rd = instr[1][1:-1]  # $ and ,
            imm = int(instr[2])
            self.r.write(rd, imm)
        elif opcode == 'add':
            # add rd, rs, rt
            rd = instr[1][1:-1]
            rs = self.r.read(instr[2][1:-1])
            rt = self.r.read(instr[3][1:])
            self.r.write(rd, rs + rt)
        elif opcode == 'addi':
            # addi rd, rs, imm
            rd = instr[1][1:-1]
            rs = self.r.read(instr[2][1:-1])
            rt = int(instr[3])
            self.r.write(rd, rs + rt)
        elif opcode == 'lw':
            # lw rt, offs(rs)
            rd = instr[1][1:-1]
            offs = int(instr[2].split('(')[0])
            addr = self.r.read(re.split('[()]', instr[2])[1][1:]) + offs
            read = struct.unpack('<I', self.m.read(addr, 4))[0]
            self.r.write(rd, read)
        elif opcode == 'sw':
            # sw rs, offs(rs)
            rd = self.r.read(instr[1][1:-1])
            offs = int(instr[2].split('(')[0])
            addr = self.r.read(re.split('[()]', instr[2])[1][1:]) + offs
            self.m.write(addr, struct.pack('<I', rd))
        else:
            raise Exception('bad instruction')

    def dump(self):
        self.r.dump()
        self.m.dump()


def main():
    cpu = CPU(16)
    if len(sys.argv) != 2:
        print 'usage'
        sys.exit(1)

    with open(sys.argv[1]) as f:
        for line in filter(None, f.readlines()):
            cpu.execute(line)

    cpu.dump()

if __name__ == '__main__':
    main()
