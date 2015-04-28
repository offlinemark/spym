import re
import sys
import struct

from registers import Registers
from memory import Memory


class CPU(object):
    def __init__(self, mem):
        self.r = Registers()
        self.m = Memory(mem)

    def execute(self, instr):
        if instr.name == 'li':
            # li rd, imm
            rd = instr.ops[0]
            imm = int(instr.ops[1])
            self.r.write(rd, imm)
        elif instr.name == 'add':
            # add rd, rs, rt
            rd = instr.ops[0]
            rs = self.r.read(instr.ops[1])
            rt = self.r.read(instr.ops[2])
            self.r.write(rd, rs + rt)
        elif instr.name == 'addi':
            # addi rd, rs, imm
            rd = instr.ops[0]
            rs = self.r.read(instr.ops[1])
            rt = int(instr.ops[2])
            self.r.write(rd, rs + rt)
        elif instr.name == 'lw':
            # lw rt, offs(rs)
            rd = instr.ops[0]
            offs = int(instr.ops[1].split('(')[0])
            addr = self.r.read(re.split('[()]', instr.ops[1])[1][1:]) + offs
            read = struct.unpack('<I', self.m.read(addr, 4))[0]
            self.r.write(rd, read)
        elif instr.name == 'sw':
            # sw rs, offs(rs)
            rd = self.r.read(instr.ops[0])
            offs = int(instr.ops[1].split('(')[0])
            addr = self.r.read(re.split('[()]', instr.ops[1])[1][1:]) + offs
            self.m.write(addr, struct.pack('<I', rd))
        elif instr.name == 'move':
            # move rd, rs
            self.r.write(instr.ops[0], self.r.read(instr.ops[1]))
        elif instr.name == 'syscall':
            # syscall
            id = self.r.read('v0')
            if id == 10:
                # exit
                print '*** exiting ***'
                sys.exit()
            elif id == 1:
                # print_int
                print self.r.read('a0'),
            elif id == 5:
                # read_int
                try:
                    inp = int(raw_input())
                    self.r.write('v0', inp)
                except Exception:
                    raise Exception('input not integer')
            else:
                raise Exception('bad syscall id')

        else:
            raise Exception('bad instruction')

    def dump(self):
        self.r.dump()
        self.m.dump()
