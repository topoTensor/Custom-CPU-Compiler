; created at 25/6/25. Simple test program.
; load 255 fibonacci numbers into ram

lli r1, 1  ; x=1
lli r2, 2  ; y=2
lli r3, 0  ; n=0
lli r5, 255 ; max_n=32

loop:
    add r4, r2, r1 ; z = x+y
    add r1, r0, r2 ; x = y
    add r2, r0, r4 ; y = z

    sw r3, r4, 0   ; save z into ram

    addi r3, r3, 1 ; n = n - 1

    bneq r3, r5, loop   ; loop back if n != max_n

