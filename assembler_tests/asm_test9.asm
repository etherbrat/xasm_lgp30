; asm_test9.asm
; test tab expansion for source files with tabs
; positives
; a comment can contain a colon: like this
start:	b	0	; a comment
				; a comment by itself
		b	0	; yet another
label:			; yet another
; try different spacing
label1:		b		0	; a comment
						; a comment by itself
			b		0	; yet another
label2:					; yet another
; just use spaces
label3: b 0 ; comment
            ; a comment by itself
        b 0 ; yet another
label4:     ; yet another
; use minimal whitespace
label5:b 0;comment - still works
; negatives
 label6:    ; label must be at the start of the line
	label7: ; ditto with a tab
;
; .end with tabs
			.end	start
 