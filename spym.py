#!/usr/bin/env python2.7

import re
import argparse

from emu.cpu import CPU, labeltab
from emu.instruction import Instruction
from emu.memory import Memory


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


def get_args():
    parser = argparse.ArgumentParser(description='Spym MIPS Interpreter. Starts in interactive shell mode, unless given MIPS source file as argument.')
    parser.add_argument('file', metavar='FILE', type=str,
                        help='MIPS source file', nargs='?')
    parser.add_argument('--memory', type=int, help='Data memory size',
                        default=64)
    return parser.parse_args()


def main():
    args = get_args()
    cpu = CPU(Memory(args.memory))

    if args.file:
        with open(args.file) as f:
            raw_imem = f.readlines()
        cpu.imem = process_imem(raw_imem)
        cpu.start()
    else:
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
