import pickle
import struct

from emu.cpu import labeltab, datatab
from util.misc import get_section

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


class SPYMHeader(object):

    def __init__(self, sections=None, binary=None):
        """Construct header either from source (sections dict) or from binary
        buffer. If both are given, it will go with sections.
        """

        self.magic = SPYM_MAGIC
        # there's always text, and it's always right after the header
        self.text_off = 20
        self.text_size = 0
        self.data_off = 0
        self.data_size = 0

        if sections:
            self._from_sections(sections)
        elif binary:
            self._from_binary(binary)

    def _from_sections(self, sections):
        """Set header fields, given a dict of the schema
        {'text': bytearray, 'data': bytearray, 'dtab': dict}.
        """

        offset = self.text_off
        for section in sections:
            size = len(sections[section])
            if section == 'text':
                self.text_size = size
            elif section == 'data':
                self.data_size = size
                self.data_off = offset
            else:
                raise Exception('bad section')
            offset += size

    def _from_binary(self, binary):
        hdr = struct.unpack('<4s4I', binary)
        if hdr[0] != self.magic:
            raise Exception('bad magic')
        elif len(hdr) != 5:
            raise Exception('bad header')

        self.text_off = hdr[1]
        self.text_size = hdr[2]
        self.data_off = hdr[3]
        self.data_size = hdr[4]

    def to_binary(self):
        return struct.pack('<4s4I', self.magic, self.text_off, self.text_size,
                           self.data_off, self.data_size)

    def dump(self):
        print 'SPYM Header:'
        self._dumpln('Magic', self.magic.encode('hex'))
        self._dumpln('Text Start', self.text_off)
        self._dumpln('Text Size', self.text_size)
        self._dumpln('Data Start', self.data_off)
        self._dumpln('Data Size', self.data_size)

    def _dumpln(self, label, value):
        print '  {}{}'.format((label + ':').ljust(20), value)


def assemble(fname):
    """Generates a spym binary given a MIPS source filename.

    struct header {
        char[4];
        size_t text_offset;
        size_t text_size;
        size_t data_offset;
        size_t data_size;
    }
    """

    with open(fname) as f:
        source = f.readlines()
    sections = {}
    body = ''

    dseg, tseg = parse.segments(source)

    # need to call parse.data first so datatab can be populated and used by
    # parse.text_binary when it needs to resolve
    sections['data'] = parse.data(dseg) if dseg else dseg
    sections['text'] = parse.text_binary(tseg)

    header = SPYMHeader(sections=sections)
    for section in sections.keys():
        body += sections[section]

    return header.to_binary() + body


def disassemble(raw):
    hdr = SPYMHeader(binary=raw[:20])
    text = parse.bin2text_list(get_section(raw, hdr.text_off, hdr.text_size))
    print '\nDisassembly:\n'
    for each in text:
        print each.raw
