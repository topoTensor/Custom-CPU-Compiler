main:
    addi    r1, r0, 6433       ; a = 6433
    addi    r2, r0, 5153       ; b = 5153

gcd_loop:
    seqz    r3, r2           ; b == 0?
    bneq    r3, r0, done     ; exit if true
    add     r4, r2, r0       ; t = b
    rem     r2, r1, r2       ; b = a % b
    add     r1, r4, r0       ; a = t
    j       gcd_loop

done:
