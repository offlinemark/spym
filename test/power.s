# reads number from stdin and computes pow(num, num) and prints

.text
main:
    li $v0, 5
    syscall
    li $t0, 1
    move $t1, $v0

cond:
    bne $t1, $zero, body
    j end

body:
    mult $t0, $v0
    mflo $t0
    addi $t1, $t1, -1
    j cond

end:
    li $v0, 1
    move $a0, $t0
    syscall

