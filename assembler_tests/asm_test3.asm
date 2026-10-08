; asm_test3.asm
; .word tests with expressions
; positives
.word 0
.word 23+14      ; LSB will be set to zero
.word 37//2      ; integer division (floor)
.word 2**31      ; should come through unscathed
.word 2**32      ; will be chopped and LSB will be set to zero
.word 0x0f0f0f0f ; LSB will be set to zero
.word 0xf0f0f0f0 ; should come through unscathed
.word -37//2     ; will be chopped and LSB will be set to zero
.word -1025      ; will be chopped and LSB will be set to zero
.word -(2**31+1) ; will be chopped and LSB will be set to zero
.word -2**32     ; will be chopped and LSB will be set to zero
; negatives
.word 23.5       ; non-integer
.word 37/2       ; non-integer
