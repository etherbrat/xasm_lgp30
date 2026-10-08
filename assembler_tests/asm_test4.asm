; asm_test4.asm
; tests of .atq without and with expressions
; there is a separate manual test of the atq python functions
; positives
.atq 3.1415927 3      ; 3243f6b4 from the programming class notes
.atq 6 3              ; 60000000
.atq -6 3             ; a0000000
.atq 6 16             ; 00030000
.atq -6 16            ; fffd0000
.atq 6 30             ; 0000000c
.atq -6 30            ; fffffff4
.atq 100000000.0 28   ; 2faf0800 big number
.atq -100000000.0 28  ; d050f800 big negative number
;
.atq 0.875 0   ; 70000000
.atq -0.875 0  ; 90000000
.atq 0.875 15  ; 0000e000
.atq -0.875 15 ; ffff2000
.atq 0.875 30  ; 00000000
.atq -0.875 30 ; fffffffe (sort of, maybe)
;
.atq (6**2)-30 (3**2)-6      ; as above
.atq -100*1000*1000 4*7      ; as above
; negatives
.atq 6 -1      ; bad q value
.atq 6 31      ; bad q value
.atq 6 2       ; non-fractional at q = 2
