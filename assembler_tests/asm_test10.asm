; asm_test10.asm
; test expression parser/evaluator operators and functions
; positives
.equ s1 2**2    ; 4
.equ s2 2*3     ; 6
.equ s3 6//4    ; 1
.equ s4 -6//4   ; -2
.equ s5 6/4     ; 1.5
.equ s6 16+8    ; 24
.equ s7 16-8    ; 8
.equ s8 -16     ; -16
.equ s9 and(0xffffffff,0x11111111) ; 0x11111111
.equ s10 or(0x0,0x1)               ; 0x1
.equ s11 xor(0x0,0x1)              ; 0x1
.equ s12 not(0x0)                  ; 0xffffffff / -1
.equ s13 shl(0x4,0x1)              ; 0x8
.equ s14 shr(0x4,0x1)              ; 0x2
.equ s15 max(8,16,32)              ; 32
.atq 3.0/6.0 1 ; special case - floating point expression 0.5 at q = 1 0x2000000
.end 0
