#!/usr/bin/env python2.7

import re
import struct
import argparse

from emu.cpu import CPU, labeltab, datatab
from emu.instruction import Instruction
from emu.memory import Memory

TYPE_TAB = {
    ".ascii":  None,
    ".asciiz": None,
    ".byte": 1,
    ".space": 1,
    ".halfword": 2,
    ".word": 4
}


def get_imm(imm):
    return int(imm, 16) if imm.startswith('0x') else int(imm)


def parse_data(data_segment):
    """Parses the .text segment source. Populates CPU datatab addresses of
    labels.

    Args:
        text_segment: list of lines, including directive

    Returns:
        bytearray representing data segment in memory, with variables declared
        later towards the beginning (lower in memory)
    """

    dseg = bytearray()
    offset = 0

    for each in data_segment[1:]:
        label, ty, decls = tuple(each.split(None, 2))

        label = label.split(':')[0]
        size = TYPE_TAB[ty]
        decls = map(lambda x: x.strip(), decls.split(','))

        datatab[label] = offset

        for decl in decls:
            if '.ascii' in ty:
                str = decl.split('"')[1]
                dseg += str
                offset += len(str)
                if ty.endswith('z'):
                    dseg += '\x00'
                    offset += 1
            else:
                if ty == '.byte':
                    dseg += struct.pack('<b', get_imm(decl))
                elif ty == '.space':
                    dseg += '\x00'*size
                elif ty == '.halfword':
                    # use big endian because we're going to reverse the whole
                    # bytearray at the end and flip it to little endian
                    dseg += struct.pack('<h', get_imm(decl))
                elif ty == '.word':
                    # re: big endian, see above
                    dseg += struct.pack('<i', get_imm(decl))
                else:
                    raise Exception('bad declaration type')
                offset += size

    # at this point offset contains the complete size of the data section,
    # and we can use that to transform the datatab values from data section
    # offsets to absolute addresses
    for each in datatab:
        datatab[each] = offset - datatab[each]

    dseg.reverse()
    return dseg


def parse_text(text_segment):
    """Parses the .text segment source

    Args:
        text_segment: list of lines, including directive

    Returns:
        list of Instructions
    """

    label_regex = re.compile('^\w+:$')
    processed_labels = 0
    imem = []
    for i, each in enumerate(text_segment[1:]):

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
            imem.append(Instruction(each))

    return imem


def generate_memory(source, dmem_size):
    directive_regex = re.compile('^\s*.(data|text)\s*$')
    dmem = Memory(dmem_size)
    imem = []

    # filter out empty lines and comments and strip everything else
    source = map(lambda x: x.strip(),
                 filter(lambda x: x.strip() and not x.strip().startswith('#'),
                        source))

    directs = filter(directive_regex.match, source)

    if '.text' not in directs:
        raise Exception('no .text directive found')
    elif len(directs) > 2 or len(directs) < 1:
        raise Exception('too many/too few segment directives')

    if len(directs) == 1:
        # it's text
        if source[0] != '.text':
            raise Exception('.text directive must be first line')
        imem = parse_text(source)
    else:
        # it's text and data
        first = source.index(directs[0])
        second = source.index(directs[1])
        # we've partitioned but we don't know which is which
        split = source[first:second], source[second:]
        split = split if split[0][0] == '.text' else split[::-1]

        imem = parse_text(split[0])
        dmem.memory = parse_data(split[1]) + dmem.memory

    return dmem, imem


def get_args():
    parser = argparse.ArgumentParser(description='Spym MIPS Interpreter. Starts in interactive shell mode, unless given MIPS source file as argument.')
    parser.add_argument('file', metavar='FILE', type=str,
                        help='MIPS source file', nargs='?')
    parser.add_argument('--memory', type=int, help='Data memory size',
                        default=64)
    return parser.parse_args()


def main():
    args = get_args()

    if args.file:
        with open(args.file) as f:
            source = f.readlines()
        cpu = CPU(*generate_memory(source, args.memory))
        cpu.start()
    else:
        cpu = CPU(Memory(args.memory))
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
