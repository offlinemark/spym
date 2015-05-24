from emu.cpu import labeltab, datatab
from emu.instruction import Instruction, BinaryInstruction


def line2val(line):
    return Instruction(line).to_binary()[0].value


def line2multi(line):
    return map(lambda x: x.value, Instruction(line).to_binary())


def test_to_binary():
    assert line2val('add $t1, $t1, $t2') == 0x12a4820
    assert line2val('addu $t1, $t1, $t2') == 0x12a4821
    assert line2val('addi $t1, $t1, -1') == 0x2129ffff
    assert line2val('addiu $t1, $t1, -1') == 0x2529ffff
    assert line2val('sub $t1, $t1, $t2') == 0x012a4822
    assert line2val('and $t1, $t1, $t2') == 0x12a4824
    assert line2val('andi $t1, $t2, 3') == 0x31490003
    assert line2val('or $t1, $t1, $t2') == 0x012a4825
    assert line2val('ori $t1, $t1, 3') == 0x35290003
    assert line2val('xor $t1, $t1, $t2') == 0x012a4826
    assert line2val('xori $t1, $t1, 3') == 0x39290003
    assert line2val('sll $t1, $t1, 3') == 0x948c0
    assert line2val('srl $t1, $t1, 4') == 0x94902
    assert line2val('sllv $t1, $t1, $t2') == 0x1494804
    assert line2val('srlv $t1, $t1, $t2') == 0x1494806
    assert line2val('slt $t1, $t1, $t2') == 0x12a482a
    assert line2val('slti $t1, $t1, 3') == 0x29290003

    labeltab['label'] = 7
    datatab['dat'] = 6
    # didn't exactly do what mars said because the imm section for these tests
    # will always be 0x0007 b/c there are no prior pseudoinstructions to
    # offset
    assert line2val('beq $t1, $t2, label') == 0x112a0007
    assert line2val('bne $t1, $t2, label') == 0x152a0007
    assert line2multi('blt $t1, $t2, label') == [0x12a082a, 0x14200007]
    assert line2multi('bgt $t1, $t2, label') == [0x149082a, 0x14200007]
    assert line2multi('ble $t1, $t2, label') == [0x149082a, 0x10200007]
    assert line2multi('bge $t1, $t2, label') == [0x12a082a, 0x10200007]
    assert line2val('j label') == 0x8000007
    assert line2val('jal label') == 0xc000007
    assert line2val('jr $t1') == 0x1200008
    assert line2val('jalr $t1') == 0x120f809
    assert line2val('lb $t1, 0($t1)') == 0x81290000
    assert line2val('lbu $t1, 0($t1)') == 0x91290000
    assert line2val('lh $t1, 0($t1)') == 0x85290000
    assert line2val('lhu $t1, 0($t1)') == 0x95290000
    assert line2val('lw $t1, 0($t1)') == 0x8d290000
    assert line2val('lui $t1, 3') == 0x3c090003
    assert line2val('li $t1, 3') == 0x24090003
    assert line2multi('la $t1, dat') == [0x3c010000, 0x34290006]
    assert line2val('sb $t0, 0($sp)') == 0xa3a80000
    assert line2val('sh $t0, 0($sp)') == 0xa7a80000
    assert line2val('sw $t0, 0($sp)') == 0xafa80000
    assert line2val('move $t1, $t0') == 0x84821
    assert line2val('div $t0, $t1') == 0x109001a
    assert line2val('mult $t0, $t1') == 0x1090018
    assert line2val('mul $t2, $t0, $t1') == 0x71095002
    assert line2val('mfhi $t0') == 0x4010
    assert line2val('mflo $t0') == 0x4012
    assert line2val('syscall') == 0xc


def test_bini():
    b = BinaryInstruction(0x12a4820)
    assert b.get_opcode() == 0
    assert b.get_rs() == 9
    assert b.get_rt() == 10
    assert b.get_rd() == 9
    assert b.get_rd() == 9
    assert b.get_funct() == 0x20
    b = BinaryInstruction(0x2129ffff)
    assert b.get_iimm() == -1
    b = BinaryInstruction(0x948c0)
    assert b.get_shamt() == 3
    b = BinaryInstruction(0x8000007)
    assert b.get_jimm() == 7


def bin2instr(bin):
    return BinaryInstruction(bin).to_instruction().raw


def test_to_instruction():
    assert bin2instr(0x12a4820) == 'add $9, $9, $10'
    assert bin2instr(0x12a4821) == 'addu $9, $9, $10'
    assert bin2instr(0x2129ffff) == 'addi $9, $9, -1'
    assert bin2instr(0x012a4822) == 'sub $9, $9, $10'
    assert bin2instr(0x12a4824) == 'and $9, $9, $10'
    assert bin2instr(0x31490003) == 'andi $9, $10, 3'
    assert bin2instr(0x012a4825) == 'or $9, $9, $10'
    assert bin2instr(0x35290003) == 'ori $9, $9, 3'
    assert bin2instr(0x012a4826) == 'xor $9, $9, $10'
    assert bin2instr(0x39290003) == 'xori $9, $9, 3'
    assert bin2instr(0x948c0) == 'sll $9, $9, 3'
    assert bin2instr(0x94902) == 'srl $9, $9, 4'
    assert bin2instr(0x1494804) == 'sllv $9, $9, $10'
    assert bin2instr(0x1494806) == 'srlv $9, $9, $10'
    assert bin2instr(0x12a482a) == 'slt $9, $9, $10'
    assert bin2instr(0x29290003) == 'slti $9, $9, 3'

    assert bin2instr(0x112a0007) == 'beq $9, $10, 7'
    assert bin2instr(0x152a0007) == 'bne $9, $10, 7'
    assert bin2instr(0x8000007) == 'j 7'
    assert bin2instr(0xc000007) == 'jal 7'
    assert bin2instr(0x1200008) == 'jr $9'
    assert bin2instr(0x120f809) == 'jalr $9'
    assert bin2instr(0x81290000) == 'lb $9, 0($9)'
    assert bin2instr(0x91290000) == 'lbu $9, 0($9)'
    assert bin2instr(0x85290000) == 'lh $9, 0($9)'
    assert bin2instr(0x95290000) == 'lhu $9, 0($9)'
    assert bin2instr(0x8d290000) == 'lw $9, 0($9)'
    assert bin2instr(0x3c090003) == 'lui $9, 3'
    assert bin2instr(0xa3a80000) == 'sb $8, 0($29)'
    assert bin2instr(0xa7a80000) == 'sh $8, 0($29)'
    assert bin2instr(0xafa80000) == 'sw $8, 0($29)'
    assert bin2instr(0x109001a) == 'div $8, $9'
    assert bin2instr(0x1090018) == 'mult $8, $9'
    assert bin2instr(0x71095002) == 'mul $10, $8, $9'
    assert bin2instr(0x4010) == 'mfhi $8'
    assert bin2instr(0x4012) == 'mflo $8'
    assert bin2instr(0xc) == 'syscall'
