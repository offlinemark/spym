#!/usr/bin/env python2.7

import argparse

from util.assemble import SPYMHeader, SPYM_HDR_LEN, disassemble


def get_args():
    parser = argparse.ArgumentParser(description='Display information about SPYM format files.')
    parser.add_argument('file', metavar='FILE', type=str,
                        help='SPYM binary')
    return parser.parse_args()


def main():
    args = get_args()
    with open(args.file) as f:
        hdr = SPYMHeader(binary=f.read(SPYM_HDR_LEN))
        hdr.dump()
        f.seek(0)
        disassemble(f.read())

if __name__ == '__main__':
    main()
