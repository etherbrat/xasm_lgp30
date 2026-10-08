; asm_test7.asm
; tests of .lshn and .rshm
        .locn 100
start:
; positives
        .lshn 1        ; 0x00000002
        .lshn 15       ; 0x00008000
        .lshn 30       ; 0x40000000
        .rshm 1        ; 0x40000000
        .rshm 15       ; 0x00010000
        .rshm 30       ; 0x00000002
; negatives
        .lshn -1       ; bad shift
        .lshn 10.      ; non-integer
        .lshn 31       ; bad shift
        .lshn 2&34//## ; bad expression
; negatives
        .rshm -1       ; bad shift
        .rshm 10.      ; non-integer
        .rshm 31       ; bad shift
        .rshm 2&34//## ; bad expression
;
       .end start