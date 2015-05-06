import parse
import pickle
import struct

from emu.cpu import labeltab, datatab


def assemble(source):
    """Generates a spym binary given f.readlines() of a MIPS source file.

    struct header {
        char[4];
        size_t text_offset;
        size_t text_size;
        size_t data_offset;
        size_t data_size;
        size_t ltab_offset;
        size_t ltab_size;
        size_t dtab_offset;
        size_t dtab_size;
    }
    """
    header = bytearray('SPYM' + struct.pack('<IIIIIIII', *[0]*8))
    body = ''
    offset = len(header)
    i = 4
    sections = []

    dseg, tseg = parse.segments(source)

    sections.append(parse.text_binary(tseg))
    sections.append(parse.data(dseg))
    sections.append(pickle.dumps(labeltab, pickle.HIGHEST_PROTOCOL))
    sections.append(pickle.dumps(datatab, pickle.HIGHEST_PROTOCOL))

    for section in sections:
        header[i:i+4] = struct.pack('<I', offset)
        header[i+4:i+8] = struct.pack('<I', len(section))
        offset += len(section)
        body += section
        i += 8

    return header + body
