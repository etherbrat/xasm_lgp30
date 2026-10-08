; echo.asm
; Echo characters received from the keyboard in 6-bit mode
; Set mode to 6-bit before running
; Terminate each character with a stop code (')
; Do NOT type more than one character before the stop code
;
.locn 3737              ; any old location
;
start:
    c harmless          ; dump then clear A/ac
    p 0                 ; start proceedings
    i 0                 ; get input - 6 bits in the lowest part of A/ac
    n shift2track       ; left shift bits to track
    a pinstr            ; drop on a p instruction
    h do_print          ; store the instr to be executed
do_print:
    .word 0             ; print
    u start             ; loop
;
shift2track:    .lshn 8 ; value to left shift 8 bits using n mult
pinstr:         p 0     ; p instruction with 0 code
harmless:       .word 0 ; some place to dump A/ac contents
;
.end start
