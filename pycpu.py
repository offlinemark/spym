import sys

from registers import Registers


class CPU(object):
    def __init__(self):
        self.r = Registers()

    def execute(self, line):
        instr = line.split()
        opcode = instr[0]
        if opcode == 'li':
            # li $1, 3
            dest = instr[1][1:-1]  # $ and ,
            src = int(instr[2])
            self.r.write(dest, src)


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
