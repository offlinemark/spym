import pickle
import struct

from emu.cpu import labeltab, datatab

SPYM_MAGIC = 'SPYM'

#
# Assembler State
#

# pseudoinstructions that translate to >1 hardware instructions.
# key = instruction name, value = # extra instructions it adds
pseudoinstructions = {'blt': 1, 'bgt': 1, 'ble': 1, 'bge': 1, 'la': 1}

# pseudoinstruction table. keeps track of addresses where pseudoinstructions
# occur, and their cost (# added instructions)
pseudotab = {}

resolved_labels = []


def resolve(label):
    """Given label, return address in instruction memory of the label.
    """

    orig_addr = labeltab[label]
    # if we haven't already resolved this label
    if label not in resolved_labels:
        # for every pseudoinstruction that precedes the label
        for addr in [addr for addr in pseudotab.keys() if addr < orig_addr]:
            # increment it's address by the number of extra instructions
            # caused by the pseudoinstruction
            labeltab[label] += pseudotab[addr]
        resolved_labels.append(label)

    return labeltab[label]


# another stupid hack to bypass circular import problems. parse needs
# the globals above
import parse


def assemble(fname):
    """Generates a spym binary given a MIPS source filename.

    struct header {
        char[4];
        size_t text_offset;
        size_t text_size;
        size_t data_offset;
        size_t data_size;
        size_t dtab_offset;
        size_t dtab_size;
    }
    """

    with open(fname) as f:
        source = f.readlines()
    header = bytearray(SPYM_MAGIC + struct.pack('<IIIIII', *[0]*6))
    body = ''
    offset = len(header)
    i = 4
    sections = []

    dseg, tseg = parse.segments(source)

    sections.append(parse.text_binary(tseg))
    sections.append(parse.data(dseg) if dseg else dseg)
    sections.append(pickle.dumps(datatab, pickle.HIGHEST_PROTOCOL))

    for section in sections:
        header[i:i+4] = struct.pack('<I', offset)
        header[i+4:i+8] = struct.pack('<I', len(section))
        offset += len(section)
        body += section
        i += 8

    return header + body
