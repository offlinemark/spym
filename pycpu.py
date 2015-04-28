import sys

registers = [0 for _ in xrange(32)]


def execute(line):
    instr = line.split()
    opcode = instr[0]
    if opcode == 'li':
        # li $1, 3
        target = int(instr[1][1:-1])  # $ and ,
        toput = int(instr[2])
        registers[target] = toput


def dump():
    for i, each in enumerate(registers):
        print '${} : {}'.format(i, each)


def main():
    if len(sys.argv) != 2:
        print 'usage'
        sys.exit(1)

    with open(sys.argv[1]) as f:
        for line in f.readlines():
            execute(line)

    dump()

if __name__ == '__main__':
    main()
