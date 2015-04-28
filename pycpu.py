import sys



class Registers:
    def __init__(self):
        self.registers = [0 for _ in xrange(32)]
        self.regtab = {
            'v0': 2,
            'v1': 3,
        }

    def read(self, reg):
        ind = reg if type(reg) is int else self.regtab[reg]
        return self.registers[ind]

    def write(self, reg, contents):
        ind = reg if type(reg) is int else self.regtab[reg]
        self.registers[ind] = contents

    def dump(self):
        for i, each in enumerate(self.registers):
            print '${} : {}\t\t'.format(i, each)


R = Registers()


def execute(line):
    instr = line.split()
    opcode = instr[0]
    if opcode == 'li':
        # li $1, 3
        dest = int(instr[1][1:-1])  # $ and ,
        src = int(instr[2])
        R.write(dest, src)




def main():
    if len(sys.argv) != 2:
        print 'usage'
        sys.exit(1)

    with open(sys.argv[1]) as f:
        for line in f.readlines():
            execute(line)

    R.dump()

if __name__ == '__main__':
    main()
