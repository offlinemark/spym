import sys

from registers import Registers


class CPU(object):
    def __init__(self):
        self.r = Registers()

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
        else:
            raise Exception('bad instruction')


def main():
    cpu = CPU()
    if len(sys.argv) != 2:
        print 'usage'
        sys.exit(1)

    with open(sys.argv[1]) as f:
        for line in filter(None, f.readlines()):
            cpu.execute(line)

    cpu.r.dump()

if __name__ == '__main__':
    main()
