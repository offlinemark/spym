#!/usr/bin/env python2.7

import sys

from cpu import CPU
from instruction import Instruction
from memory import Memory

MEM_SIZE = 16


def main():
    cpu = CPU(Memory(MEM_SIZE))

    if len(sys.argv) != 2:
        while True:
            inp = raw_input('spym > ').strip()
            if inp == 'exit':
                break
            elif inp == 'dump':
                cpu.dump()
                continue
            elif not inp:
                continue

            try:
                cpu.execute_single(Instruction(inp))
            except Exception, e:
                if e.message == 'exit syscall':
                    break
                raise e
    else:
        if sys.argv[1] in ['-h', '--help']:
            print 'usage: {} [-h] [FILE]'
            print """Spym MIPS Interpreter. Starts in interactive shell mode, unless given MIPS
source file as argument."""
            sys.exit()

        with open(sys.argv[1]) as f:
            imem = f.readlines()
        imem = filter(lambda x: x.strip() and not x.strip().startswith('#'),
                      imem)
        imem = map(lambda x: Instruction(x.strip()), imem)
        cpu.imem = imem
        cpu.start()

    cpu.dump()

if __name__ == '__main__':
    main()
