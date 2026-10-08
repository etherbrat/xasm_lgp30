; asm_test5.asm
; labels and address arithmetic
; positives
           .locn 100
start:     c 0
           b datastart
           .locn 200
           .atq numdata 3
           .locn 1000
datastart: .atq 0.5 0
           .atq 0.5 1
           .atq 0.5 2
           .atq 0.5 3
dataend:
           .equ numdata dataend-datastart
; negatives
           .locn 5000                    ; bad location
           .locn 2000
           .equ new_symbol location1+200 ; forward reference
location1: .word 0
;
           .end start+1                  ; should be ok
