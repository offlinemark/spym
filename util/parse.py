import re
import struct

from emu.cpu import labeltab, datatab
from emu.instruction import Instruction, BinaryInstruction
from util.misc import get_imm
from util.assemble import pseudotab, pseudoinstructions

TYPE_TAB = {
    ".ascii":  None,
    ".asciiz": None,
    ".byte": 1,
    ".space": 1,
    ".halfword": 2,
    ".word": 4
}


def data(data_segment):
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

        for decl in decls[::-1]:
            if '.ascii' in ty:
                if ty.endswith('z'):
                    dseg += '\x00'
                    offset += 1
                str = decl.split('"')[1][::-1]
                dseg += str
                offset += len(str)
            else:
                if ty == '.byte':
                    dseg += struct.pack('>b', get_imm(decl))
                elif ty == '.space':
                    dseg += '\x00'*size
                elif ty == '.halfword':
                    # use big endian because we're going to reverse the whole
                    # bytearray at the end and flip it to little endian
                    dseg += struct.pack('>h', get_imm(decl))
                elif ty == '.word':
                    # re: big endian, see above
                    dseg += struct.pack('>i', get_imm(decl))
                else:
                    raise Exception('bad declaration type')
                offset += size

        datatab[label] = offset

    # at this point offset contains the complete size of the data section,
    # and we can use that to transform the datatab values from data section
    # offsets to absolute addresses
    for each in datatab:
        datatab[each] = offset - datatab[each]

    dseg.reverse()
    return dseg


def text_list(text_segment):
    """Parses the .text segment source

    Args:
        text_segment: list of lines, including .text directive

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


def text_binary(text_segment):
    global pseudotab
    imem = bytearray()
    # strip .text directive at text_segment[0]
    text_segment = text_segment[1:]

    # initializes labeltab, removes labels from text_segment
    text_segment = _init_labeltab(text_segment)
    # then when we resolved labels we look in the pseudotab for all instrs with addrs less than label and all their costs to label addr

    for addr, line in enumerate(text_segment):
        instr = Instruction(line)
        # if we found a pseudoinstruction
        if instr.name in pseudoinstructions.iterkeys():
            # add entry to pseudotab with its cost (# added instructions)
            pseudotab[addr] = pseudoinstructions[instr.name]
        for bini in instr.to_binary():
            imem += struct.pack('>I', bini.value)

    return imem


def _init_labeltab(text_segment):
    """Helper function for populating labeltab structure with labels and their
    addresses in instruction memory while removing those labels from the
    input text_segment

    Args:
        text_segment: list of instruction lines, not including .text directive
    """

    processed_labels = 0
    label_regex = re.compile('^\w+:$')

    for addr, line in enumerate(text_segment):
        if label_regex.match(line):
            key = line.split(':')[0]
            if key in labeltab:
                raise Exception('label already used')
            # i here indexes into a list containing labels, however those
            # labels will not be present in the final list. to ensure that
            # the imem address stored in labeltab refers to the correct
            # index in the final list, subtract it by the number of labels
            # that occur above the current one which have been artifically
            # increasing the index
            labeltab[key] = addr - processed_labels
            processed_labels += 1
            text_segment[addr] = None

    return [x for x in text_segment if x is not None]


def segments(source):
    """Parses out the .data and .text segments given the f.readlines() of
    the MIPS source file.
    """

    directive_regex = re.compile('^\s*.(data|text)\s*$')

    # filter out empty lines and comments and strip everything else
    source = map(lambda x: x.split('#')[0].strip(),
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
        return '', source
    else:
        # it's text and data
        first = source.index(directs[0])
        second = source.index(directs[1])
        # we've partitioned but we don't know which is which
        split = source[first:second], source[second:]
        if split[0][0] == '.text':
            split = split[::-1]

        return split


def bin2text_list(binary):
    text_list = []
    for bini in [binary[i:i+4] for i in range(0, len(binary), 4)]:
        value = struct.unpack('>I', bini)[0]
        text_list.append(BinaryInstruction(value).to_instruction())
    return text_list
