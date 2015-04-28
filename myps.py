import sys

from cpu import CPU
from instruction import Instruction

MEMORY = 16


def main():
    if len(sys.argv) != 2:
        print 'Usage: {} <file>'
        sys.exit(1)

    cpu = CPU(MEMORY)

    with open(sys.argv[1]) as f:
        for _line in f.readlines():
            line = _line.strip()
            if line and not line.startswith('#'):
                cpu.execute(Instruction(line))

    cpu.dump()

if __name__ == '__main__':
    main()
