#!/usr/bin/env python2.7

import argparse

from util.assemble import assemble


def get_args():
    parser = argparse.ArgumentParser(description='Spym MIPS Assembler. Generates "spym" format binaries.')
    parser.add_argument('file', metavar='FILE', type=str,
                        help='MIPS source file')
    parser.add_argument('-o', '--output', type=str,
                        help='File to write output to. Default is a.out',
                        default='a.out')
    return parser.parse_args()


def main():
    args = get_args()
    with open(args.output, 'w') as f:
        f.write(assemble(args.file))

if __name__ == '__main__':
    main()
