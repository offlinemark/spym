# Factorial Program (using memory) by Mark Mossberg
# Uses data section to store an int 5, computes factorial, and prints to
# stdout.

# Pseudocode:
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
    li $v0, 10
    syscall
