import binascii
import logging as log


def hexdump(buffer, to_log=False):
    fmt = '{:04x}: {}{} {}{}  {} {}'

    for i in range(0, len(buffer), 8):
        word = buffer[i:i+4] if i <= len(buffer) - 4 else buffer[i:]
        word2 = buffer[i+4:i+8] if i <= len(buffer) - 8 else buffer[i+4:]

        out = fmt.format(i, binascii.hexlify(word), _pad(word),
                         binascii.hexlify(word2), _pad(word2),
                         _print_version(word),
                         _print_version(word2))

        if to_log:
            log.info(out)
        else:
            print out


def _pad(str):
    # str is the 4 byte string, occupying 8 characters when hexlified.
    return ' ' * (8-len(str)*2)


def _print_version(word):
    ret = ''
    for char in word:
        ret += chr(char) if char > 0x20 and char < 0x7f else '.'
    return ret
