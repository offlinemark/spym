from emu.instruction import Instruction


def line2val(line):
    return Instruction(line).to_binary()[0].value


def test_to_binary():
    assert line2val('add $t1, $t1, $t2') == 0x12a4820
    assert line2val('addi $t1, $t2, 3') == 0x21490003
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
