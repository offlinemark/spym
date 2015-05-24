# Why this file exists:
# This file exists because of the circular dependency between emu.instruction
# and util.parse. doing any sort of `from util.parse import` in emu.instruction
# will fail because util.parse also requires emu.instruction.Instruction
# however, but that hasn't been loaded yet at import time. So we use this
# shared file instead. Alternatively, all the `from util.parse import` lines
# could go beneath the Instruction class declaration, but that's messy


def get_imm(imm):
    return int(imm, 16) if imm.startswith('0x') else int(imm)


def get_section(raw, off, size):
    return raw[off:off+size]
