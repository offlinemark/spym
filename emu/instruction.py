import re

from emu.cpu import labeltab
from emu.registers import regmap

# number of extra instructions caused by pseudo instruction expansion
pseudocount = 0


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
        bin = BinaryInstruction()
        if self.name == 'add':
            # add rd, rs, rt
            bin.set_funct(0x20)
            bin.set_rd(regmap(self.ops[0]))
            bin.set_rs(regmap(self.ops[1]))
            bin.set_rt(regmap(self.ops[2]))
        elif self.name == 'addi':
            # addi rd, rs, imm
            bin.set_opcode(0x8)
        elif self.name == 'sub':
            # sub rd, rs, rt
            bin.set_funct(0x22)
        elif self.name == 'and':
            # and rd, rs, rt
            bin.set_funct(0x24)
        elif self.name == 'andi':
            # andi rd, rs, imm
            bin.set_opcode(0xc)
        elif self.name == 'or':
            # or rd, rs, rt
            bin.set_funct(0x25)
        elif self.name == 'ori':
            # ori rd, rs, imm
            bin.set_opcode(0xd)
        elif self.name == 'xor':
            # xor rd, rs, rt
            bin.set_funct(0x26)
        elif self.name == 'xori':
            # xori rd, rs, imm
            bin.set_opcode(0xe)
        elif self.name == 'sll':
            # sll rd, rs, shamt
            pass
        elif self.name == 'srl':
            # srl rd, rs, shamt
            bin.set_funct(0x2)
        elif self.name == 'sllv':
            # sllv rd, rs, rt
            bin.set_funct(0x4)
        elif self.name == 'srlv':
            # srlv rd, rs, rt
            bin.set_funct(0x6)
        elif self.name == 'slt':
            # slt rd, rs, rt
            bin.set_funct(0x2a)
        elif self.name == 'slti':
            # slti rd, rs, imm
            bin.set_opcode(0xa)
        elif self.name == 'beq':
            # beq rs, rt, label
            bin.set_opcode(0x4)
        elif self.name == 'bne':
            # bne rs, rt, label
            bin.set_opcode(0x5)
        elif self.name == 'blt':
            # pseudo: blt rs, rt, label
            # slt $1, rs, rt
            # bne $1, $zero, label
            slt = Instruction('slt $1, ${}, ${}'.format(self.ops[0],
                                                        self.ops[1])).to_binary()[0]
            bins.append(slt)
            bin = Instruction('bne $1, $0, {}'.format(self.ops[2])).to_binary()[0]
            pseudocount += 1
        elif self.name == 'bgt':
            # pseudo: bgt rs, rt, label
            # slt $1, rt, rs
            # bne $1, $zero, label
            slt = Instruction('slt $1, ${}, ${}'.format(self.ops[1],
                                                        self.ops[0])).to_binary()[0]
            bins.append(slt)
            bin = Instruction('bne $1, $0, {}'.format(self.ops[2])).to_binary()[0]
            pseudocount += 1
        elif self.name == 'ble':
            # pseudo: ble rs, rt, label
            # slt $1, rt, rs
            # beq $1, $zero, label
            slt = Instruction('slt $1, ${}, ${}'.format(self.ops[1],
                                                        self.ops[0])).to_binary()[0]
            bins.append(slt)
            bin = Instruction('beq $1, $0, {}'.format(self.ops[2])).to_binary()[0]
            pseudocount += 1
        elif self.name == 'bge':
            # pseudo: bge rs, rt, label
            # slt $1, rs, rt
            # beq $1, $zero, label
            slt = Instruction('slt $1, ${}, ${}'.format(self.ops[0],
                                                        self.ops[1])).to_binary()[0]
            bins.append(slt)
            bin = Instruction('beq $1, $0, {}'.format(self.ops[2])).to_binary()[0]
            pseudocount += 1
        elif self.name == 'j':
            # j label
            bin.set_opcode(0x2)
            bin.set_imm(labeltab[self.ops[0]] + pseudocount)
        elif self.name == 'jal':
            # jal label
            bin.set_opcode(0x3)
            bin.set_imm(labeltab[self.ops[0]] + pseudocount)
        elif self.name == 'jr':
            # jr rs
            bin.set_funct(0x8)
            bin.set_rs(regmap(self.ops[0]))
        elif self.name == 'jalr':
            # jalr rs
            bin.set_funct(0x9)
        elif self.name == 'lb':
            # lb rt, offs(rs)
            bin.set_opcode(0x20)
        elif self.name == 'lbu':
            # lbu rt, offs(rs)
            bin.set_opcode(0x24)
        elif self.name == 'lh':
            # lh rt, offs(rs)
            bin.set_opcode(0x21)
        elif self.name == 'lhu':
            # lhu rt, offs(rs)
            bin.set_opcode(0x25)
        elif self.name == 'lw':
            # TODO: lw will always treat that memory as signed, even when it
            # potentially should be unsigned? With sw we can detect if they're
            # trying to write a negative number and change the struct.pack
            # arg accordingly, but with lw, we have no indication

            # lw rt, offs(rs)
            bin.set_opcode(0x23)
        elif self.name == 'lui':
            # lui rt, imm
            bin.set_opcode(0xf)
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
            raise Exception('bad selfuction')
        
        bins.append(bin)
        return bins


class BinaryInstruction(object):
    def __init__(self):
        self.value = 0

    def set_opcode(self, opcode):
        self._set_or_shift(opcode, 26)

    def set_rs(self, rs):
        self._set_or_shift(rs, 21)

    def set_rt(self, rt):
        self._set_or_shift(rt, 16)

    def set_rd(self, rd):
        self._set_or_shift(rd, 11)

    def set_shamt(self, shamt):
        self._set_or_shift(shamt, 6)

    def set_funct(self, funct):
        self.set_imm(funct)

    def set_imm(self, imm):
        self.value |= imm

    def _set_or_shift(self, num, shift):
        self.value |= (num << shift)
