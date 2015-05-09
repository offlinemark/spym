import re

from emu.cpu import labeltab
from emu.registers import regmap

# number of extra instructions caused by pseudo instruction expansion
pseudocount = 0


def get_imm(imm):
    return int(imm, 16) if imm.startswith('0x') else int(imm)


class Instruction(object):
    def __init__(self, line):
        instr = line.split(' ')
        self.raw = line
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

    def to_binary(self):
        """Returns instruction as list of 32 bit words. It's a list because of
        pseudo instructions which aren't real hardware instructions, but rather
        convenience builtins provided by the assembler.
        """

        bins = []
        bini = BinaryInstruction()
        if self.name == 'add':
            # add rd, rs, rt
            bini.set_arith(0x20, self.ops)
        elif self.name == 'addi':
            # addi rt, rs, imm
            bini.set_arith_imm(0x8, self.ops)
        elif self.name == 'sub':
            # sub rd, rs, rt
            bini.set_arith(0x22, self.ops)
        elif self.name == 'and':
            # and rd, rs, rt
            bini.set_arith(0x24, self.ops)
        elif self.name == 'andi':
            # andi rt, rs, imm
            bini.set_arith_imm(0xc, self.ops)
        elif self.name == 'or':
            # or rd, rs, rt
            bini.set_arith(0x25, self.ops)
        elif self.name == 'ori':
            # ori rt, rs, imm
            bini.set_arith_imm(0xd, self.ops)
        elif self.name == 'xor':
            # xor rd, rs, rt
            bini.set_arith(0x26, self.ops)
        elif self.name == 'xori':
            # xori rt, rs, imm
            bini.set_arith_imm(0xe, self.ops)
        elif self.name == 'sll':
            # sll rd, rt, shamt
            bini.set_rd(self.ops[0])
            bini.set_rt(self.ops[1])
            bini.set_shamt_str(self.ops[2])
        elif self.name == 'srl':
            # srl rd, rt, shamt
            bini.set_funct(0x2)
            bini.set_rd(self.ops[0])
            bini.set_rt(self.ops[1])
            bini.set_shamt_str(self.ops[2])
        elif self.name == 'sllv':
            # sllv rd, rt, rs
            bini.set_funct(0x4)
            bini.set_rd(self.ops[0])
            bini.set_rt(self.ops[1])
            bini.set_rs(self.ops[2])
        elif self.name == 'srlv':
            # srlv rd, rt, rs
            bini.set_funct(0x6)
            bini.set_rd(self.ops[0])
            bini.set_rt(self.ops[1])
            bini.set_rs(self.ops[2])
        elif self.name == 'slt':
            # slt rd, rs, rt
            bini.set_arith(0x2a, self.ops)
        elif self.name == 'slti':
            # slti rd, rs, imm
            bini.set_arith_imm(0xa, self.ops)
        elif self.name == 'beq':
            # beq rs, rt, label
            bini.set_opcode(0x4)
        elif self.name == 'bne':
            # bne rs, rt, label
            bini.set_opcode(0x5)
        elif self.name == 'blt':
            # pseudo: blt rs, rt, label
            # slt $1, rs, rt
            # bne $1, $zero, label
            slt = Instruction('slt $1, ${}, ${}'.format(self.ops[0],
                                                        self.ops[1])).to_binary()[0]
            bins.append(slt)
            bini = Instruction('bne $1, $0, {}'.format(self.ops[2])).to_binary()[0]
            pseudocount += 1
        elif self.name == 'bgt':
            # pseudo: bgt rs, rt, label
            # slt $1, rt, rs
            # bne $1, $zero, label
            slt = Instruction('slt $1, ${}, ${}'.format(self.ops[1],
                                                        self.ops[0])).to_binary()[0]
            bins.append(slt)
            bini = Instruction('bne $1, $0, {}'.format(self.ops[2])).to_binary()[0]
            pseudocount += 1
        elif self.name == 'ble':
            # pseudo: ble rs, rt, label
            # slt $1, rt, rs
            # beq $1, $zero, label
            slt = Instruction('slt $1, ${}, ${}'.format(self.ops[1],
                                                        self.ops[0])).to_binary()[0]
            bins.append(slt)
            bini = Instruction('beq $1, $0, {}'.format(self.ops[2])).to_binary()[0]
            pseudocount += 1
        elif self.name == 'bge':
            # pseudo: bge rs, rt, label
            # slt $1, rs, rt
            # beq $1, $zero, label
            slt = Instruction('slt $1, ${}, ${}'.format(self.ops[0],
                                                        self.ops[1])).to_binary()[0]
            bins.append(slt)
            bini = Instruction('beq $1, $0, {}'.format(self.ops[2])).to_binary()[0]
            pseudocount += 1
        elif self.name == 'j':
            # j label
            bini.set_opcode(0x2)
            bini.set_imm(labeltab[self.ops[0]] + pseudocount)
        elif self.name == 'jal':
            # jal label
            bini.set_opcode(0x3)
            bini.set_imm(labeltab[self.ops[0]] + pseudocount)
        elif self.name == 'jr':
            # jr rs
            bini.set_funct(0x8)
            bini.set_rs(regmap(self.ops[0]))
        elif self.name == 'jalr':
            # jalr rs
            bini.set_funct(0x9)
        elif self.name == 'lb':
            # lb rt, offs(rs)
            bini.set_opcode(0x20)
        elif self.name == 'lbu':
            # lbu rt, offs(rs)
            bini.set_opcode(0x24)
        elif self.name == 'lh':
            # lh rt, offs(rs)
            bini.set_opcode(0x21)
        elif self.name == 'lhu':
            # lhu rt, offs(rs)
            bini.set_opcode(0x25)
        elif self.name == 'lw':
            # TODO: lw will always treat that memory as signed, even when it
            # potentially should be unsigned? With sw we can detect if they're
            # trying to write a negative number and change the struct.pack
            # arg accordingly, but with lw, we have no indication

            # lw rt, offs(rs)
            bini.set_opcode(0x23)
        elif self.name == 'lui':
            # lui rt, imm
            bini.set_opcode(0xf)
        elif self.name == 'li':
            # li rd, imm
            pass
        elif self.name == 'la':
            # la rd, label
            pass
        elif self.name == 'sb':
            # sb rt, offs(rs)
            pass





        # we might not actually need the labeltab in the binary now that the
        # jump labels can be easily resolved


        elif self.name == 'sh':
            # sb rt, offs(rs)
            pass
        elif self.name == 'sw':
            # sw rt, offs(rs)
            pass
        elif self.name == 'move':
            # move rd, rs
            pass
        elif self.name == 'div':
            # div rs, rt
            pass
        elif self.name == 'mult':
            # mult rs, rt
            pass
        elif self.name == 'mfhi':
            # mfhi rd
            pass
        elif self.name == 'mflo':
            # mfhi rd
            pass
        elif self.name == 'syscall':
            # syscall
            pass
        else:
            raise Exception('bad instruction')

        bins.append(bini)
        return bins


class BinaryInstruction(object):
    def __init__(self):
        self.value = 0

    def set_arith(self, funct, ops):
        self.set_funct(funct)
        self.set_rd(ops[0])
        self.set_rs(ops[1])
        self.set_rt(ops[2])

    def set_arith_imm(self, opcode, ops):
        self.set_opcode(opcode)
        self.set_rt(ops[0])
        self.set_rs(ops[1])
        self.set_imm_str(ops[2])

    def set_opcode(self, opcode):
        self._or_shift(opcode, 26)

    def set_rs(self, rsstr):
        self._set_rs(regmap(rsstr))

    def set_rt(self, rtstr):
        self._set_rt(regmap(rtstr))

    def set_rd(self, rdstr):
        self._set_rd(regmap(rdstr))

    def set_shamt_int(self, shamt):
        self._or_shift(shamt, 6)

    def set_shamt_str(self, shamt):
        self.set_shamt_int(get_imm(shamt))

    def set_funct(self, funct):
        self.set_imm_int(funct)

    def set_imm_int(self, imm):
        self.value |= imm

    def set_imm_str(self, immstr):
        self.set_imm_int(get_imm(immstr))

    def _set_rs(self, rs):
        self._or_shift(rs, 21)

    def _set_rt(self, rt):
        self._or_shift(rt, 16)

    def _set_rd(self, rd):
        self._or_shift(rd, 11)

    def _or_shift(self, num, shift):
        self.value |= (num << shift)
