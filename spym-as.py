#!/usr/bin/env python2.7

import argparse

import assemble
import util


def get_args():
    parser = argparse.ArgumentParser(description='Spym MIPS Assembler. Generates "spym" format binaries.')
    parser.add_argument('file', metavar='FILE', type=str,
                        help='MIPS source file')
    return parser.parse_args()


def main():
    args = get_args()
    fname = args.file
    if fname.endswith('.s'):
        fname = fname[-2:] + '.spym'
    else:
        fname = fname + '.spym'
    # with open(fname, 'w') as f:
    with open(args.file) as ff:
        util.hexdump(assemble.assemble(ff.readlines()))

if __name__ == '__main__':
    main()
