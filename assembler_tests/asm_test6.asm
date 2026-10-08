; asm_test6.asm
; .blkw tests
; positives
start:  .blkw 5              ; allocate 5
next:   .blkw 7+3            ; allocate 10
after:  .blkw next-start     ; ok - no forward reference
last:
; negatives
        .blkw diff           ; blows up in pass 1 - no allocation
        .equ diff next-start ; evaluated in pass 1
wrong:                       ; gets wrong value in pass 1
        .end start
