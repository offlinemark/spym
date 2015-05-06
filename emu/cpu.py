import sys
import struct

from registers import Registers

labeltab = {}
datatab = {}


class CPU(object):
    def __init__(self, dmem, imem=None):
        self.r = Registers(dmem.size())
        self.dmem = dmem
        self.imem = imem

    def start(self, debug):
        print '=== CPU Start===\n'

        if debug:
            last = ''
            cmds = ['?', '(p)rint $reg', '(c)ontinue', '(d)ump', '(n)ext',
                    '(q)uit']
            print "*** debug mode enabled. '?' for help ***\n"

        if self.imem is None:
            raise Exception('imem not set')

        while self.r.pc in xrange(len(self.imem)):
            instr = self.imem[self.r.pc]
            try:
                print '[{}] {}'.format(self.r.pc, instr.raw)
                if debug:
                    while True:
                        inp = raw_input('(debug) ').strip()

                        if not inp:
                            inp = last
                        else:
                            last = inp

                        if inp == '?':
                            print 'Commands:', ', '.join(cmds)
                        elif inp in ['d', 'dump']:
                            self.dump()
                        elif inp in ['c', 'continue']:
                            debug = False
                            break
                        elif inp in ['n', 'next']:
                            break
                        elif inp in ['q', 'quit']:
                            sys.exit()
                        elif inp.split()[0] in ['p', 'print']:
                            print self.r.read(inp.split()[1][1:])
                        else:
                            print 'Bad Command'
                self.execute_single(instr)
            except Exception, e:
                if e.message == 'exit syscall':
                    return
                raise e
            self.r.pc += 1
        print '\n*** pc [{}] outside instruction memory ***'.format(self.r.pc)

    def execute_single(self, instr):
        if instr.name == 'add':
            # add rd, rs, rt
            rd = instr.ops[0]
            rs = self.r.read(instr.ops[1])
            rt = self.r.read(instr.ops[2])
            self.r.write(rd, rs + rt)
        elif instr.name == 'addi':
            # addi rd, rs, imm
            rd = instr.ops[0]
            rs = self.r.read(instr.ops[1])
            imm = self._get_imm(instr.ops[2])
            self.r.write(rd, rs + imm)
        elif instr.name == 'sub':
            # sub rd, rs, rt
            rd = instr.ops[0]
            rs = self.r.read(instr.ops[1])
            rt = self.r.read(instr.ops[2])
            self.r.write(rd, rs - rt)
        elif instr.name == 'and':
            # and rd, rs, rt
            rd = instr.ops[0]
            rs = self.r.read(instr.ops[1])
            rt = self.r.read(instr.ops[2])
            self.r.write(rd, rs & rt)
        elif instr.name == 'andi':
            # andi rd, rs, imm
            rd = instr.ops[0]
            rs = self.r.read(instr.ops[1])
            imm = self._get_imm(instr.ops[2])
            self.r.write(rd, rs & imm)
        elif instr.name == 'or':
            # or rd, rs, rt
            rd = instr.ops[0]
            rs = self.r.read(instr.ops[1])
            rt = self.r.read(instr.ops[2])
            self.r.write(rd, rs | rt)
        elif instr.name == 'ori':
            # ori rd, rs, imm
            rd = instr.ops[0]
            rs = self.r.read(instr.ops[1])
            imm = self._get_imm(instr.ops[2])
            self.r.write(rd, rs | imm)
        elif instr.name == 'xor':
            # xor rd, rs, rt
            rd = instr.ops[0]
            rs = self.r.read(instr.ops[1])
            rt = self.r.read(instr.ops[2])
            self.r.write(rd, rs ^ rt)
        elif instr.name == 'xori':
            # xori rd, rs, imm
            rd = instr.ops[0]
            rs = self.r.read(instr.ops[1])
            imm = self._get_imm(instr.ops[2])
            self.r.write(rd, rs ^ imm)
        elif instr.name == 'sll':
            # sll rd, rs, shamt
            rd = instr.ops[0]
            rs = self.r.read(instr.ops[1])
            shamt = self._get_imm(instr.ops[2])
            self.r.write(rd, rs << shamt)
        elif instr.name == 'srl':
            # srl rd, rs, shamt
            rd = instr.ops[0]
            rs = self.r.read(instr.ops[1])
            shamt = self._get_imm(instr.ops[2])
            self.r.write(rd, rs >> shamt)
        elif instr.name == 'sllv':
            # sllv rd, rs, rt
            rd = instr.ops[0]
            rs = self.r.read(instr.ops[1])
            rt = self.r.read(instr.ops[2])
            self.r.write(rd, rs << rt)
        elif instr.name == 'srlv':
            # srlv rd, rs, rt
            rd = instr.ops[0]
            rs = self.r.read(instr.ops[1])
            rt = self.r.read(instr.ops[2])
            self.r.write(rd, rs >> rt)
        elif instr.name == 'slt':
            # slt rd, rs, rt
            tmp = 1 if self.r.read(instr.ops[1]) < self.r.read(instr.ops[2]) else 0
            self.r.write(instr.ops[0], tmp)
        elif instr.name == 'slti':
            # slti rd, rs, imm
            rs = instr.ops[1]
            imm = self._get_imm(instr.ops[2])
            tmp = 1 if self.r.read(rs) < imm else 0
            self.r.write(instr.ops[0], tmp)
        elif instr.name == 'beq':
            # beq rs, rt, label
            if (self.r.read(instr.ops[0]) == self.r.read(instr.ops[1])):
                self._set_pc_label(instr.ops[2])
        elif instr.name == 'bne':
            # bne rs, rt, label
            if (self.r.read(instr.ops[0]) != self.r.read(instr.ops[1])):
                self._set_pc_label(instr.ops[2])
        elif instr.name == 'blt':
            # blt rs, rt, label
            if (self.r.read(instr.ops[0]) < self.r.read(instr.ops[1])):
                self._set_pc_label(instr.ops[2])
        elif instr.name == 'bgt':
            # bgt rs, rt, label
            if (self.r.read(instr.ops[0]) > self.r.read(instr.ops[1])):
                self._set_pc_label(instr.ops[2])
        elif instr.name == 'ble':
            # ble rs, rt, label
            if (self.r.read(instr.ops[0]) <= self.r.read(instr.ops[1])):
                self._set_pc_label(instr.ops[2])
        elif instr.name == 'bge':
            # bge rs, rt, label
            if (self.r.read(instr.ops[0]) >= self.r.read(instr.ops[1])):
                self._set_pc_label(instr.ops[2])
        elif instr.name == 'j':
            # j label
            self._set_pc_label(instr.ops[0])
        elif instr.name == 'jal':
            # jal label
            self.r.write('ra', self.r.pc + 1)
            self._set_pc_label(instr.ops[0])
        elif instr.name == 'jr':
            # jr rs
            self._set_pc(self.r.read(instr.ops[0]))
        elif instr.name == 'jalr':
            # jalr rs
            self.r.write('ra', self.r.pc + 1)
            self._set_pc(self.r.read(instr.ops[0]))
        elif instr.name == 'lb':
            # lb rt, offs(rs)
            rt = instr.ops[0]
            offs = self._get_imm(instr.ops[1])
            addr = self.r.read(instr.ops[2]) + offs
            read = struct.unpack('<b', self.dmem.read(addr, 1))[0]
            self.r.write(rt, read)
        elif instr.name == 'lbu':
            # lbu rt, offs(rs)
            rt = instr.ops[0]
            offs = self._get_imm(instr.ops[1])
            addr = self.r.read(instr.ops[2]) + offs
            read = struct.unpack('<B', self.dmem.read(addr, 1))[0]
            self.r.write(rt, read)
        elif instr.name == 'lh':
            # lh rt, offs(rs)
            rt = instr.ops[0]
            offs = self._get_imm(instr.ops[1])
            addr = self.r.read(instr.ops[2]) + offs
            read = struct.unpack('<h', self.dmem.read(addr, 2))[0]
            self.r.write(rt, read)
        elif instr.name == 'lhu':
            # lhu rt, offs(rs)
            rt = instr.ops[0]
            offs = self._get_imm(instr.ops[1])
            addr = self.r.read(instr.ops[2]) + offs
            read = struct.unpack('<H', self.dmem.read(addr, 2))[0]
            self.r.write(rt, read)
        elif instr.name == 'lw':
            # TODO: lw will always treat that memory as signed, even when it
            # potentially should be unsigned? With sw we can detect if they're
            # trying to write a negative number and change the struct.pack
            # arg accordingly, but with lw, we have no indication

            # lw rt, offs(rs)
            rd = instr.ops[0]
            offs = self._get_imm(instr.ops[1])
            addr = self.r.read(instr.ops[2]) + offs
            read = struct.unpack('<I', self.dmem.read(addr, 4))[0]
            self.r.write(rd, read)
        elif instr.name == 'lui':
            # lui rt, imm
            rt = instr.ops[0]
            imm = self._get_imm(instr.ops[1])
            self.r.write(rt, (imm << 16) & 0xffffffff)
        elif instr.name == 'li':
            # li rd, imm
            rd = instr.ops[0]
            imm = self._get_imm(instr.ops[1])
            self.r.write(rd, imm)
        elif instr.name == 'la':
            # la rd, label
            rd = instr.ops[0]
            label = instr.ops[1]
            self.r.write(rd, datatab[label])
        elif instr.name == 'sb':
            # sb rt, offs(rs)
            rt = self.r.read(instr.ops[0])
            offs = self._get_imm(instr.ops[1])
            addr = self.r.read(instr.ops[2]) + offs
            self.dmem.write(addr, struct.pack('<b' if rt < 0 else '<B', rt))
        elif instr.name == 'sh':
            # sb rt, offs(rs)
            rt = self.r.read(instr.ops[0])
            offs = self._get_imm(instr.ops[1])
            addr = self.r.read(instr.ops[2]) + offs
            self.dmem.write(addr, struct.pack('<h' if rt < 0 else '<H', rt))
        elif instr.name == 'sw':
            # sw rt, offs(rs)
            rt = self.r.read(instr.ops[0])
            offs = self._get_imm(instr.ops[1])
            addr = self.r.read(instr.ops[2]) + offs
            self.dmem.write(addr, struct.pack('<i' if rt < 0 else '<I', rt))
        elif instr.name == 'move':
            # move rd, rs
            self.r.write(instr.ops[0], self.r.read(instr.ops[1]))
        elif instr.name == 'div':
            # div rs, rt
            rs = self.r.read(instr.ops[0])
            rt = self.r.read(instr.ops[1])
            self.r.lo = rs / rt
            self.r.hi = rs % rt
        elif instr.name == 'mult':
            # mult rs, rt
            rs = self.r.read(instr.ops[0])
            rt = self.r.read(instr.ops[1])
            mult = (rs * rt) & 0xffffffffffffffff
            self.r.hi = mult >> 32
            self.r.lo = mult & 0xffffffff
        elif instr.name == 'mfhi':
            # mfhi rd
            self.r.write(instr.ops[0], self.r.hi)
        elif instr.name == 'mflo':
            # mfhi rd
            self.r.write(instr.ops[0], self.r.lo)
        elif instr.name == 'syscall':
            # syscall
            id = self.r.read('v0')
            if id == 10:
                # exit
                print '\n*** exiting ***'
                raise Exception('exit syscall')
            elif id == 1:
                # print_int
                print self.r.read('a0'),
            elif id == 5:
                # read_int
                try:
                    inp = int(raw_input())
                    self.r.write('v0', inp)
                except Exception:
                    raise Exception('input not integer')
            else:
                raise Exception('bad syscall id')

        else:
            raise Exception('bad instruction')

    def dump(self):
        print '\n=== CPU Dump ==='
        print '\nRegisters\n'
        self.r.dump()
        print '\nData Memory\n'
        self.dmem.dump()

    def _set_pc_label(self, label):
        self._set_pc(labeltab[label])

    def _set_pc(self, value):
        # the -1 is because pc is automatically incremented 1 when this
        # returns
        self.r.pc = value - 1

    def _get_imm(self, imm):
        return int(imm, 16) if imm.startswith('0x') else int(imm)
