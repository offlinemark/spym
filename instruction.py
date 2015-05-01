import re

class Instruction(object):
    def __init__(self, line):
        instr = line.split(' ')
        self.name = instr[0]
        self.ops = []

        if len(instr) > 4:
            raise Exception('too many operands: {}'.format(line))

        # iterate through operands, perform some loose checks, and append
        # to self.ops
        for each in instr[1:]:
            if each.endswith(','):
                each = each[:-1]
            if each.startswith('$'):
                each = each[1:]
            if '(' in each:
                each = each.replace('$', '')
                self.ops += re.split('[()]', each)[:-1]
            else:
                self.ops.append(each)
