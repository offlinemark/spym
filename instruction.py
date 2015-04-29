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
            self.ops.append(each[1:] if each.startswith('$') else each)
