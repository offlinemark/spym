class Registers(object):
    regc = 32
    regtab = {
        'v0': 2, 'v1': 3,
        'a0': 4, 'a1': 5, 'a2': 6, 'a3': 7,
        't0': 8, 't1': 9, 't2': 10, 't3': 11, 't4': 12, 't5': 13, 't6': 14, 't7': 15,
        's0': 16, 's1': 17, 's2': 18, 's3': 19, 's4': 20, 's5': 21, 's6': 22, 's7': 23,
        't8': 24, 't9': 25,
        'k0': 26, 'k1': 27,
        'gp': 28,
        'sp': 29,
        'fp': 30,
        'ra': 31,
        'zero': 0
    }

    def __init__(self):
        self.registers = [0] * self.regc
        self.pc = 0

    def read(self, reg):
        ind = int(reg) if reg[0].isdigit() else self.regtab[reg]
        return self.registers[ind]

    def write(self, reg, contents):
        ind = int(reg) if reg[0].isdigit() else self.regtab[reg]
        if ind == 0:
            raise Exception('can\'t write to $zero')
        self.registers[ind] = contents

    def dump(self):
        for reg in sorted(self.regtab):
            print '${}/{} : {}\t\t'.format(reg, self.regtab[reg],
                                           self.registers[self.regtab[reg]])
