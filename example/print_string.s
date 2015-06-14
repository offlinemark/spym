# Declares "hello" and '!' '!' '!' in the data section, and prints "hello".

.text
    la $a0, str
    li $v0, 4
    syscall

.data
blah: .byte 0x21, 0x21, 0x21
str: .asciiz "hello"
