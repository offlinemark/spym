# spym

A MIPS ISA toolchain including a (dis)assembler, debugger, and runtime.

The following utilities are included:

- `spym`: The spym virtual machine, emulating a subset of the MIPS ISA. Capable
  of executing MIPS assembly source files *and* binaries produced by `spasm`.
  Includes a basic GDB-style debugger and REPL mode.
- `spasm`: The spym assembler. Produces SPYM format binaries.
- `spread`: The spym reader. Displays information about and disassembles SPYM
  binaries.

> Note: spym does not include a lexer or parser, because they are outside the
> scope of this learning exercise. Thus, it does not perform any kind of syntax
> validation and will likely crash if you give it poorly formatted code. You
> have been warned.

## Usage

```
$ ./spym -h
usage: spym [-h] [--stack STACK] [--debug] [-v] [--assemble] [FILE]

Spym MIPS Interpreter. Starts in interactive shell mode, unless given MIPS
source file as argument.

positional arguments:
  FILE           MIPS source file

optional arguments:
  -h, --help     show this help message and exit
  --stack STACK  Stack memory size. Default: 64 bytes
  --debug        Activate debugger. Implies verbose.
  -v, --verbose  Verbose output
  --assemble     Assemble file into SPYM binary format rather than execute.
                 Overrides other arguments.

$ ./spasm -h
usage: spasm [-h] [-o OUTPUT] FILE

Spym MIPS Assembler. Generates "spym" format binaries.

positional arguments:
  FILE                  MIPS source file

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        File to write output to. Default is a.out

$ ./spread -h
usage: spread [-h] FILE

Display information about SPYM format files.

positional arguments:
  FILE        SPYM binary

optional arguments:
  -h, --help  show this help message and exit
```

## Example

```
$ cat test.s
# mips factorial calculator

# pseudo-C:
#
# int input = 5;
#
# main() {
#     int count = input;
#     int tmp = 1;
#
#     while (count) {
#         tmp *= count;
#         count--;
#     }
#
#     print_int(tmp);
# }

.data
input: .word 5

.text

main:
    addi $sp, $sp, -8
    move $t0, $sp  # count
    addi $t1, $sp, 4  # tmp

    la $s0, input
    lw $s0, 0($s0)

    sw $s0, 0($t0)
    li $t3, 1
    sw $t3, 0($t1)

cond:
    lw $t3, 0($t0)
    bne $t3, $zero, body
    j end

body:
    lw $t4, 0($t1)
    mult $t4, $t3
    mflo $t5
    sw $t5, 0($t1)
    addi $t3, $t3, -1
    sw $t3, 0($t0)
    j cond

end:
    li $v0, 1
    lw $t2, 0($t1)
    move $a0, $t2
    syscall
$ ./spym.py test.s --stack 8 -v
=== CPU Start===

[0] addi $sp, $sp, -8
[1] move $t0, $sp
[2] addi $t1, $sp, 4
[3] la $s0, input
[4] lw $s0, 0($s0)
[5] sw $s0, 0($t0)
[6] li $t3, 1
[7] sw $t3, 0($t1)
[8] lw $t3, 0($t0)
[9] bne $t3, $zero, body
[11] lw $t4, 0($t1)
[12] mult $t4, $t3
[13] mflo $t5
[14] sw $t5, 0($t1)
[15] addi $t3, $t3, -1
[16] sw $t3, 0($t0)
[17] j cond
[8] lw $t3, 0($t0)
[9] bne $t3, $zero, body
[11] lw $t4, 0($t1)
[12] mult $t4, $t3
[13] mflo $t5
[14] sw $t5, 0($t1)
[15] addi $t3, $t3, -1
[16] sw $t3, 0($t0)
[17] j cond
[8] lw $t3, 0($t0)
[9] bne $t3, $zero, body
[11] lw $t4, 0($t1)
[12] mult $t4, $t3
[13] mflo $t5
[14] sw $t5, 0($t1)
[15] addi $t3, $t3, -1
[16] sw $t3, 0($t0)
[17] j cond
[8] lw $t3, 0($t0)
[9] bne $t3, $zero, body
[11] lw $t4, 0($t1)
[12] mult $t4, $t3
[13] mflo $t5
[14] sw $t5, 0($t1)
[15] addi $t3, $t3, -1
[16] sw $t3, 0($t0)
[17] j cond
[8] lw $t3, 0($t0)
[9] bne $t3, $zero, body
[11] lw $t4, 0($t1)
[12] mult $t4, $t3
[13] mflo $t5
[14] sw $t5, 0($t1)
[15] addi $t3, $t3, -1
[16] sw $t3, 0($t0)
[17] j cond
[8] lw $t3, 0($t0)
[9] bne $t3, $zero, body
[10] j end
[18] li $v0, 1
[19] lw $t2, 0($t1)
[20] move $a0, $t2
[21] syscall
120
*** pc [22] outside instruction memory ***

=== CPU Dump ===

Registers

$a0/4 : 120
$a1/5 : 0
$a2/6 : 0
$a3/7 : 0
$fp/30 : 0
$gp/28 : 0
$k0/26 : 0
$k1/27 : 0
$ra/31 : 0
$s0/16 : 5
$s1/17 : 0
$s2/18 : 0
$s3/19 : 0
$s4/20 : 0
$s5/21 : 0
$s6/22 : 0
$s7/23 : 0
$sp/29 : 4
$t0/8 : 4
$t1/9 : 8
$t2/10 : 120
$t3/11 : 0
$t4/12 : 120
$t5/13 : 120
$t6/14 : 0
$t7/15 : 0
$t8/24 : 0
$t9/25 : 0
$v0/2 : 1
$v1/3 : 0
$zero/0 : 0
pc : 22
hi : 0
lo : 120

Data/Stack Memory

0000: 05000000 00000000  .... ....
0008: 78000000           x...
```

## Debug Mode

```
$ ./spym.py test.s --stack 8 --debug -v
=== CPU Start===

*** debug mode enabled. '?' for help ***

[0] addi $sp, $sp, -8
(debug) n
[1] move $t0, $sp
(debug)
[2] addi $t1, $sp, 4
(debug)
[3] la $s0, input
(debug)
[4] lw $s0, 0($s0)
(debug)
[5] sw $s0, 0($t0)
(debug)
[6] li $t3, 1
(debug) p $s0
5
(debug) dump

=== CPU Dump ===

Registers

$a0/4 : 0
$a1/5 : 0
$a2/6 : 0
$a3/7 : 0
$fp/30 : 0
$gp/28 : 0
$k0/26 : 0
$k1/27 : 0
$ra/31 : 0
$s0/16 : 5
$s1/17 : 0
$s2/18 : 0
$s3/19 : 0
$s4/20 : 0
$s5/21 : 0
$s6/22 : 0
$s7/23 : 0
$sp/29 : 4
$t0/8 : 4
$t1/9 : 8
$t2/10 : 0
$t3/11 : 0
$t4/12 : 0
$t5/13 : 0
$t6/14 : 0
$t7/15 : 0
$t8/24 : 0
$t9/25 : 0
$v0/2 : 0
$v1/3 : 0
$zero/0 : 0
pc : 6
hi : 0
lo : 0

Data/Stack Memory

0000: 05000000 05000000  .... ....
0008: 00000000           ....
(debug) c
[7] sw $t3, 0($t1)
[8] lw $t3, 0($t0)
[9] bne $t3, $zero, body
[11] lw $t4, 0($t1)
[12] mult $t4, $t3
[13] mflo $t5
[14] sw $t5, 0($t1)
[15] addi $t3, $t3, -1
[16] sw $t3, 0($t0)
[17] j cond
[8] lw $t3, 0($t0)
[9] bne $t3, $zero, body
[11] lw $t4, 0($t1)
[12] mult $t4, $t3
[13] mflo $t5
[14] sw $t5, 0($t1)
[15] addi $t3, $t3, -1
[16] sw $t3, 0($t0)
[17] j cond
[8] lw $t3, 0($t0)
[9] bne $t3, $zero, body
[11] lw $t4, 0($t1)
[12] mult $t4, $t3
[13] mflo $t5
[14] sw $t5, 0($t1)
[15] addi $t3, $t3, -1
[16] sw $t3, 0($t0)
[17] j cond
[8] lw $t3, 0($t0)
[9] bne $t3, $zero, body
[11] lw $t4, 0($t1)
[12] mult $t4, $t3
[13] mflo $t5
[14] sw $t5, 0($t1)
[15] addi $t3, $t3, -1
[16] sw $t3, 0($t0)
[17] j cond
[8] lw $t3, 0($t0)
[9] bne $t3, $zero, body
[11] lw $t4, 0($t1)
[12] mult $t4, $t3
[13] mflo $t5
[14] sw $t5, 0($t1)
[15] addi $t3, $t3, -1
[16] sw $t3, 0($t0)
[17] j cond
[8] lw $t3, 0($t0)
[9] bne $t3, $zero, body
[10] j end
[18] li $v0, 1
[19] lw $t2, 0($t1)
[20] move $a0, $t2
[21] syscall
120
*** pc [22] outside instruction memory ***

=== CPU Dump ===

Registers

$a0/4 : 120
$a1/5 : 0
$a2/6 : 0
$a3/7 : 0
$fp/30 : 0
$gp/28 : 0
$k0/26 : 0
$k1/27 : 0
$ra/31 : 0
$s0/16 : 5
$s1/17 : 0
$s2/18 : 0
$s3/19 : 0
$s4/20 : 0
$s5/21 : 0
$s6/22 : 0
$s7/23 : 0
$sp/29 : 4
$t0/8 : 4
$t1/9 : 8
$t2/10 : 120
$t3/11 : 0
$t4/12 : 120
$t5/13 : 120
$t6/14 : 0
$t7/15 : 0
$t8/24 : 0
$t9/25 : 0
$v0/2 : 1
$v1/3 : 0
$zero/0 : 0
pc : 22
hi : 0
lo : 120

Data/Stack Memory

0000: 05000000 00000000  .... ....
0008: 78000000           x...
```
