#!/usr/bin/env python2.7

import argparse
import logging as log

import util.parse
from emu.cpu import CPU
from emu.instruction import Instruction
from emu.memory import Memory


def get_args():
    parser = argparse.ArgumentParser(description='Spym MIPS Interpreter. Starts in interactive shell mode, unless given MIPS source file as argument.')
    parser.add_argument('file', metavar='FILE', type=str,
                        help='MIPS source file', nargs='?')
    parser.add_argument('--stack', type=int, help='Stack memory size',
                        default=64)
    parser.add_argument('--debug', help='Activate debugger. Implies verbose.',
                        action='store_true')
    parser.add_argument('-v', '--verbose', help='Verbose output',
                        action='store_true')
    parser.add_argument('--assemble',
                        help='Assemble file into SPYM binary format rather than execute. Overrides other arguments.',
                        action='store_true')
    return parser.parse_args()


def main():
    args = get_args()

    lvl = log.INFO if args.verbose or args.debug else None
    log.basicConfig(format='%(message)s', level=lvl)

    if args.file:
        with open(args.file) as f:
            source = f.readlines()
        dseg, tseg = util.parse.segments(source)
        dmem = Memory(args.stack)
        if dseg:
            dmem.memory = util.parse.data(dseg) + dmem.memory
        cpu = CPU(dmem, util.parse.text_list(tseg))
        cpu.start(args.debug)
    else:
        cpu = CPU(Memory(args.stack))
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

    cpu.dump()

if __name__ == '__main__':
    main()
