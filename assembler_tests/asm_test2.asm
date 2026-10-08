; asm_test2.asm
; .locn and label tests
; positive
.locn 1000
start:
    b a
    a b
.locn 1100
a: .word 0
b: .word 0
; negative
a: ; duplicate label
.locn 5000      ; bad address
.locn -1        ; bad address
.locn 3.5       ; bad address
.locn 3000+2000 ; bad address
.locn 2&33//4d  ; bad adress expression
