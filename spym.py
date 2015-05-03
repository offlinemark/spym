#!/usr/bin/env python2.7

import re
import sys

from cpu import CPU, labeltab
from instruction import Instruction
from memory import Memory

MEM_SIZE = 16


def process_imem(raw_imem):
    label_regex = re.compile('^\w+:$')
    processed_labels = 0
    tmp = []

    # filter out empty lines and comments
    raw_imem = filter(lambda x: x.strip() and not x.strip().startswith('#'),
                      raw_imem)
    for i, each in enumerate(raw_imem):
        if label_regex.match(each):
            key = each.split(':')[0]
            if key in labeltab:
                raise Exception('label already used')
            # i here indexes into a list containing labels, however those
            # labels will not be present in the final list. to ensure that
            # the imem address stored in labeltab refers to the correct
            # index in the final list, subtract it by the number of labels
            # that occur above the current one which have been artifically
            # increasing the index
            labeltab[key] = i - processed_labels
            processed_labels += 1
        else:
            tmp.append(Instruction(each.strip()))

    return tmp


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
            raw_imem = f.readlines()
        cpu.imem = process_imem(raw_imem)
        cpu.start()

    cpu.dump()

if __name__ == '__main__':
    main()
