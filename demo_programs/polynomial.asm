; polynomial.asm
; Evaluate polynomial
; LGP-30 Programming Manual, April 1957, Pages 12-20
; Page 19, 'Final Program', excluding call to print routine
;
; Calcuate y = a0*x^4 + a1*x^3 + a2*x^2 + a3*x + a4
; Refactored as y = (((a0*x + a1)*x + a2)*x + a3)*x + a4
;
.locn 1000
start:
    b add_instr ; initial add instr
    c do_add    ; place inline and zero A/ac
    h result    ; clear intermediate value
;
loop:
    b result    ; get intermediate value
    m x         ; * x (initially 0)
do_add:
    .word 0     ; indexed add instr for execution
    h result    ; update intermediate value
;
    b do_add    ; get add instr
    a CONST_1   ; increment address
    h do_add    ; update add instr
    s end_instr ; check for end of func
    t loop      ; go back for more?
    z 0         ; end of prog - temp contains result
;
result:
    .word 0     ; result accumulated here - q value of a0*x^4
CONST_1:
    .atq 1 29   ; incrementer
add_instr:
    a a0        ; add instr with addr of first constant
end_instr:
    a end_add   ; add instr with addr past last constant
;
x:  .word 0     ; put x here using atqdeposit
a0: .word 0     ; put a0 here using atqdeposit
a1: .word 0     ; put a1 here - q value of a0*x using atqdeposit
a2: .word 0     ; put a2 here - a value of a0*x^2 using atqdeposit
a3: .word 0     ; put a3 here - q value of a0*x^3 using atqdeposit
a4: .word 0     ; put a4 here - q value of a0*x^4 using atqdeposit
end_add: .word 0    ; past last constant
;
.end start

; some test values
; x   1.2 at q = 3      -1.2 at q = 4
; a0  3.4 at q = 3      -4.3 at q = 5
; a1  5.6 at q = 6      -5.6 at q = 9
; a2  7.8 at q = 9      -8.7 at q = 13
; a3  9.0 at q = 12     -9.0 at q = 17
; a4  1.2 at q = 15     -2.1 at q = 21
; y   39.95904          -3.06768
