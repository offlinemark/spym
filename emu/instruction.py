import re
import ctypes

from emu.registers import regmap
from util.misc import get_imm
from emu.cpu import datatab


def raw_arith(name, self):
    return '{} ${}, ${}, ${}'.format(name, self.get_rd(), self.get_rs(),
                                     self.get_rt())


def raw_arith_imm(name, self):
    return '{} ${}, ${}, {}'.format(name, self.get_rt(), self.get_rs(),
                                    self.get_iimm())


def raw_branch(name, self):
    return '{} ${}, ${}, {}'.format(name, self.get_rs(), self.get_rt(),
                                    self.get_iimm())


def raw_mem(name, self):
    return '{} ${}, {}(${})'.format(name, self.get_rt(), self.get_iimm(),
                                    self.get_rs())


class Instruction(object):
    def __init__(self, line):
        instr = line.split()
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
        elif self.name == 'addu':
            # addu rd, rs, rt
            bini.set_arith(0x21, self.ops)
        elif self.name == 'addi':
            # addi rt, rs, imm
            bini.set_arith_imm(0x8, self.ops)
        elif self.name == 'addiu':
            # addiu rt, rs, imm
            bini.set_arith_imm(0x9, self.ops)
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
            bini.set_shamt(self.ops[2])
        elif self.name == 'srl':
            # srl rd, rt, shamt
            bini.set_funct(0x2)
            bini.set_rd(self.ops[0])
            bini.set_rt(self.ops[1])
            bini.set_shamt(self.ops[2])
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
            bini.set_rs(self.ops[0])
            bini.set_rt(self.ops[1])
            bini.set_imm(resolve(self.ops[2]), 0xffff)
        elif self.name == 'bne':
            # bne rs, rt, label
            bini.set_opcode(0x5)
            bini.set_rs(self.ops[0])
            bini.set_rt(self.ops[1])
            bini.set_imm(resolve(self.ops[2]), 0xffff)
        elif self.name == 'blt':
            # pseudo: blt rs, rt, label
            # slt $1, rs, rt
            # bne $1, $zero, label
            slt = Instruction('slt $1, ${}, ${}'.format(self.ops[0],
                                                        self.ops[1])).to_binary()[0]
            bins.append(slt)
            bini = Instruction('bne $1, $0, {}'.format(self.ops[2])).to_binary()[0]
        elif self.name == 'bgt':
            # pseudo: bgt rs, rt, label
            # slt $1, rt, rs
            # bne $1, $zero, label
            slt = Instruction('slt $1, ${}, ${}'.format(self.ops[1],
                                                        self.ops[0])).to_binary()[0]
            bins.append(slt)
            bini = Instruction('bne $1, $0, {}'.format(self.ops[2])).to_binary()[0]
        elif self.name == 'ble':
            # pseudo: ble rs, rt, label
            # slt $1, rt, rs
            # beq $1, $zero, label
            slt = Instruction('slt $1, ${}, ${}'.format(self.ops[1],
                                                        self.ops[0])).to_binary()[0]
            bins.append(slt)
            bini = Instruction('beq $1, $0, {}'.format(self.ops[2])).to_binary()[0]
        elif self.name == 'bge':
            # pseudo: bge rs, rt, label
            # slt $1, rs, rt
            # beq $1, $zero, label
            slt = Instruction('slt $1, ${}, ${}'.format(self.ops[0],
                                                        self.ops[1])).to_binary()[0]
            bins.append(slt)
            bini = Instruction('beq $1, $0, {}'.format(self.ops[2])).to_binary()[0]
        elif self.name == 'j':
            # j label
            bini.set_opcode(0x2)
            bini.set_imm(resolve(self.ops[0]), 0x3ffffff)
        elif self.name == 'jal':
            # jal label
            bini.set_opcode(0x3)
            bini.set_imm(resolve(self.ops[0]), 0x3ffffff)
        elif self.name == 'jr':
            # jr rs
            bini.set_funct(0x8)
            bini.set_rs(self.ops[0])
        elif self.name == 'jalr':
            # jalr rs
            bini.set_funct(0x9)
            bini.set_rs(self.ops[0])
            # TODO: support 2 operand jalr
            bini.set_rd(31)
        elif self.name == 'lb':
            # lb rt, offs(rs)
            bini.set_mem(0x20, self.ops)
        elif self.name == 'lbu':
            # lbu rt, offs(rs)
            bini.set_mem(0x24, self.ops)
        elif self.name == 'lh':
            # lh rt, offs(rs)
            bini.set_mem(0x21, self.ops)
        elif self.name == 'lhu':
            # lhu rt, offs(rs)
            bini.set_mem(0x25, self.ops)
        elif self.name == 'lw':
            # TODO: lw will always treat that memory as signed, even when it
            # potentially should be unsigned? With sw we can detect if they're
            # trying to write a negative number and change the struct.pack
            # arg accordingly, but with lw, we have no indication

            # lw rt, offs(rs)
            bini.set_mem(0x23, self.ops)
        elif self.name == 'lui':
            # lui rt, imm
            bini.set_opcode(0xf)
            bini.set_rt(self.ops[0])
            bini.set_imm(self.ops[1], 0xffff)
        elif self.name == 'li':
            # pseudo: li rd, imm
            # addiu $rd, $zero, imm
            bini = Instruction('addiu {}, $0, {}'.format(self.ops[0],
                                                         self.ops[1])).to_binary()[0]
        elif self.name == 'la':
            # pseudo: la rd, label
            # lui $1, label[31:16]
            # ori rd, $1, label[15:0]

            # TODO: current limitation of la is that it only works for labels
            # in the .data section. technically we should support .text labels
            # too. this would involved calling resolve here and unifying the
            # labeltab and datatab into a single symtab

            lui = Instruction('lui $1, 0x{:x}'.format(datatab[self.ops[1]] >> 16)).to_binary()[0]
            bins.append(lui)
            bini = Instruction('ori ${}, $1, 0x{:x}'.format(self.ops[0],
                                                            datatab[self.ops[1]] & 0xffff)).to_binary()[0]
        elif self.name == 'sb':
            # sb rt, offs(rs)
            bini.set_mem(0x28, self.ops)
        elif self.name == 'sh':
            # sh rt, offs(rs)
            bini.set_mem(0x29, self.ops)
        elif self.name == 'sw':
            # sw rt, offs(rs)
            bini.set_mem(0x2b, self.ops)
        elif self.name == 'move':
            # pseudo: move rd, rs
            # addu rd, $zero, rs
            bini = Instruction('addu ${}, $0, ${}'.format(self.ops[0],
                                                          self.ops[1])).to_binary()[0]
        elif self.name == 'div':
            # div rs, rt
            bini.set_funct(0x1a)
            bini.set_rs(self.ops[0])
            bini.set_rt(self.ops[1])
        elif self.name == 'mult':
            # mult rs, rt
            bini.set_funct(0x18)
            bini.set_rs(self.ops[0])
            bini.set_rt(self.ops[1])
        elif self.name == 'mul':
            # mul rd, rs, rt
            bini.set_opcode(0x1c)
            bini.set_funct(0x2)
            bini.set_rd(self.ops[0])
            bini.set_rs(self.ops[1])
            bini.set_rt(self.ops[2])
        elif self.name == 'mfhi':
            # mfhi rd
            bini.set_funct(0x10)
            bini.set_rd(self.ops[0])
        elif self.name == 'mflo':
            # mflo rd
            bini.set_funct(0x12)
            bini.set_rd(self.ops[0])
        elif self.name == 'syscall':
            # syscall
            bini.set_funct(0xc)
        else:
            raise Exception('bad instruction: {}'.format(self.name))

        bins.append(bini)
        return bins


# stupid hack: this import line is down here because of dumb circular import
# problems. instruction -> assemble -> parse -> instruction, and by the time
# parse tries to load Instruction, the original instruction import hasn't
# made it that far down
from util.assemble import resolve


class BinaryInstruction(object):
    masks = {'opcode': 0x3f, 'reg': 0x1f, 'shamt': 0x1f, 'funct': 0x3f,
             'imm16': 0xffff, 'imm26': 0x3ffffff}

    def __init__(self, value=0):
        self.value = value

    def set_arith(self, funct, ops):
        self.set_funct(funct)
        self.set_rd(ops[0])
        self.set_rs(ops[1])
        self.set_rt(ops[2])

    def set_arith_imm(self, opcode, ops):
        self.set_opcode(opcode)
        self.set_rt(ops[0])
        self.set_rs(ops[1])
        self.set_imm(ops[2], self.masks['imm16'])

    def set_mem(self, opcode, ops):
        self.set_opcode(opcode)
        self.set_rt(ops[0])
        self.set_imm(ops[1], self.masks['imm16'])
        self.set_rs(ops[2])

    def get_opcode(self):
        return self._get_bits(26, self.masks['opcode'])

    def set_opcode(self, opcode):
        self._or_shift(opcode, 26, self.masks['opcode'])

    def get_rs(self):
        return self._get_bits(21, self.masks['reg'])

    def set_rs(self, rs):
        try:
            self._or_shift(rs, 21, self.masks['reg'])
        except TypeError:
            self._or_shift(regmap(rs), 21, self.masks['reg'])

    def get_rt(self):
        return self._get_bits(16, self.masks['reg'])

    def set_rt(self, rt):
        try:
            self._or_shift(rt, 16, self.masks['reg'])
        except TypeError:
            self._or_shift(regmap(rt), 16, self.masks['reg'])

    def get_rd(self):
        return self._get_bits(11, self.masks['reg'])

    def set_rd(self, rd):
        try:
            self._or_shift(rd, 11, self.masks['reg'])
        except TypeError:
            self._or_shift(regmap(rd), 11, self.masks['reg'])

    def get_shamt(self):
        return self._get_bits(6, self.masks['shamt'])

    def set_shamt(self, shamt):
        try:
            self._or_shift(shamt, 6, self.masks['shamt'])
        except TypeError:
            self._or_shift(get_imm(shamt), 6, self.masks['shamt'])

    def get_funct(self):
        return self.value & self.masks['funct']

    def set_funct(self, funct):
        self.set_imm(funct & self.masks['funct'])

    def get_jimm(self):
        # j instr imm
        # semantics of the j instr means unsigned here
        return self.value & self.masks['imm26']

    def get_iimm(self):
        # i instr imm
        # need to extract bits as signed
        return ctypes.c_short(self.value & self.masks['imm16']).value

    def set_imm(self, imm, mask=0xffffffff):
        try:
            self.value |= (imm & mask)
        except TypeError:
            self.value |= (get_imm(imm) & mask)

    def _get_bits(self, shift, mask):
        return (self.value >> shift) & mask

    def _or_shift(self, num, shift, mask=0xffffffff):
        self.value |= ((num & mask) << shift)

    def to_instruction(self):
        """Returns binary instruction a proper Instruction object.
        """

        instr = None
        op = self.get_opcode()

        if op == 0:
            # arithmetic instruction
            funct = self.get_funct()
            if funct == 0x20:
                # add rd, rs, rt
                instr = Instruction(raw_arith('add', self))
            elif funct == 0x21:
                # addu rd, rs, rt
                instr = Instruction(raw_arith('addu', self))
            elif funct == 0x22:
                # sub rd, rs, rt
                instr = Instruction(raw_arith('sub', self))
            elif funct == 0x24:
                # and rd, rs, rt
                instr = Instruction(raw_arith('and', self))
            elif funct == 0x25:
                # or rd, rs, rt
                instr = Instruction(raw_arith('or', self))
            elif funct == 0x26:
                # xor rd, rs, rt
                instr = Instruction(raw_arith('xor', self))
            elif funct == 0:
                # sll rd, rt, shamt
                instr = Instruction('sll ${}, ${}, {}'.format(self.get_rd(),
                                                              self.get_rt(),
                                                              self.get_shamt()))
            elif funct == 2:
                # sll rd, rt, shamt
                instr = Instruction('srl ${}, ${}, {}'.format(self.get_rd(),
                                                              self.get_rt(),
                                                              self.get_shamt()))
            elif funct == 0x4:
                # sllv rd, rt, rs
                instr = Instruction('sllv ${}, ${}, ${}'.format(self.get_rd(),
                                                                self.get_rt(),
                                                                self.get_rs()))
            elif funct == 0x6:
                # srlv rd, rt, rs
                instr = Instruction('srlv ${}, ${}, ${}'.format(self.get_rd(),
                                                                self.get_rt(),
                                                                self.get_rs()))
            elif funct == 0x2a:
                # slt rd, rs, rt
                instr = Instruction(raw_arith('slt', self))
            elif funct == 0x8:
                # jr rs
                instr = Instruction('jr ${}'.format(self.get_rs()))
            elif funct == 0x9:
                # jalr rs
                instr = Instruction('jalr ${}'.format(self.get_rs()))
            elif funct == 0x1a:
                # div rs, rt
                instr = Instruction('div ${}, ${}'.format(self.get_rs(),
                                                          self.get_rt()))
            elif funct == 0x18:
                # mult rs, rt
                instr = Instruction('mult ${}, ${}'.format(self.get_rs(),
                                                           self.get_rt()))
            elif funct == 0x10:
                # mfhi rd
                instr = Instruction('mfhi ${}'.format(self.get_rd()))
            elif funct == 0x12:
                # mflo rd
                instr = Instruction('mflo ${}'.format(self.get_rd()))
            elif funct == 0xc:
                # syscall
                instr = Instruction('syscall')
            else:
                raise Exception('bad funct')
        elif op == 0x8:
            # addi rt, rs, imm
            instr = Instruction(raw_arith_imm('addi', self))
        elif op == 0x9:
            # addiu rt, rs, imm
            instr = Instruction(raw_arith_imm('addiu', self))
        elif op == 0xc:
            # andi rt, rs, imm
            instr = Instruction(raw_arith_imm('andi', self))
        elif op == 0xd:
            # ori rt, rs, imm
            instr = Instruction(raw_arith_imm('ori', self))
        elif op == 0xe:
            # xori rt, rs, imm
            instr = Instruction(raw_arith_imm('xori', self))
        elif op == 0xa:
            # slti rd, rs, imm
            instr = Instruction(raw_arith_imm('slti', self))
        elif op == 0x4:
            # beq rs, rt, label
            instr = Instruction(raw_branch('beq', self))
        elif op == 0x5:
            # bne rs, rt, label
            instr = Instruction(raw_branch('bne', self))
        elif op == 0x2:
            # j label
            instr = Instruction('j {}'.format(self.get_jimm()))
        elif op == 0x3:
            # j label
            instr = Instruction('jal {}'.format(self.get_jimm()))
        elif op == 0x20:
            # lb rt, offs(rs)
            instr = Instruction(raw_mem('lb', self))
        elif op == 0x24:
            # lbu rt, offs(rs)
            instr = Instruction(raw_mem('lbu', self))
        elif op == 0x21:
            # lh rt, offs(rs)
            instr = Instruction(raw_mem('lh', self))
        elif op == 0x25:
            # lhu rt, offs(rs)
            instr = Instruction(raw_mem('lhu', self))
        elif op == 0x23:
            # lw rt, offs(rs)
            instr = Instruction(raw_mem('lw', self))
        elif op == 0xf:
            # lui rt, imm
            instr = Instruction('lui ${}, {}'.format(self.get_rt(),
                                                     self.get_iimm()))
        elif op == 0x28:
            # sb rt, offs(rs)
            instr = Instruction(raw_mem('sb', self))
        elif op == 0x29:
            # sh rt, offs(rs)
            instr = Instruction(raw_mem('sh', self))
        elif op == 0x2b:
            # sw rt, offs(rs)
            instr = Instruction(raw_mem('sw', self))
        elif op == 0x1c:
            funct = self.get_funct()
            if funct == 0x2:
                # mul rd, rs, rt
                instr = Instruction('mul ${}, ${}, ${}'.format(self.get_rd(),
                                                               self.get_rs(),
                                                               self.get_rt()))
        else:
            raise Exception('bad opcode')

        return instr
