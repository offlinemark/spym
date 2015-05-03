# spym

A little Harvard architecture MIPS interpreter.

## Usage

```
usage: spym.py [-h] [--memory MEMORY] [FILE]

Spym MIPS Interpreter. Starts in interactive shell mode, unless given MIPS
source file as argument.

positional arguments:
  FILE             MIPS source file

optional arguments:
  -h, --help       show this help message and exit
  --memory MEMORY  Data memory size
```

## Example

```
$ cat test.s
# test mips program

# equivalent pseudo-C:
#
# int main() {
#     int x;
#     func(&x);
#     print_int(x);
#     exit();
# }
#
# void func(int *y) {
#     *y = 0xffff;
# }

main:
    addi $sp, $sp, -4
    move $a0, $sp
    jal func
    li $v0, 1
    lw $a0, 0($a0)
    syscall
    li $v0, 10
    syscall

func:
    li $t0, 0xffff
    sw $t0, 0($a0)
    jr $ra
$ ./spym.py --memory 8 test.s
=== CPU Start===

[0] addi $sp, $sp, -4
[1] move $a0, $sp
[2] jal func
[8] li $t0, 0xffff
[9] sw $t0, 0($a0)
[10] jr $ra
[3] li $v0, 1
[4] lw $a0, 0($a0)
[5] syscall
65535 [6] li $v0, 10
[7] syscall

*** exiting ***

=== CPU Dump ===

Registers

$a0/4 : 65535
$a1/5 : 0
$a2/6 : 0
$a3/7 : 0
$fp/30 : 0
$gp/28 : 0
$k0/26 : 0
$k1/27 : 0
$ra/31 : 3
$s0/16 : 0
$s1/17 : 0
$s2/18 : 0
$s3/19 : 0
$s4/20 : 0
$s5/21 : 0
$s6/22 : 0
$s7/23 : 0
$sp/29 : 4
$t0/8 : 65535
$t1/9 : 0
$t2/10 : 0
$t3/11 : 0
$t4/12 : 0
$t5/13 : 0
$t6/14 : 0
$t7/15 : 0
$t8/24 : 0
$t9/25 : 0
$v0/2 : 10
$v1/3 : 0
$zero/0 : 0
pc : 7

Data Memory

bytearray(b'\x00\x00\x00\x00\xff\xff\x00\x00')
```
