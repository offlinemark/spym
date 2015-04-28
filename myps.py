#!/usr/bin/env python

import sys

from cpu import CPU
from instruction import Instruction

MEMORY = 16


def main():
    cpu = CPU(MEMORY)

    if len(sys.argv) != 2:
        while True:
            inp = raw_input('myps > ').strip()
            if inp == 'exit':
                break
            elif inp == 'dump':
                cpu.dump()
                continue
            elif not inp:
                continue

            cpu.execute(Instruction(inp))
    else:
        with open(sys.argv[1]) as f:
            for _line in f.readlines():
                line = _line.strip()
                if line and not line.startswith('#'):
                    cpu.execute(Instruction(line))

    cpu.dump()

if __name__ == '__main__':
    main()
