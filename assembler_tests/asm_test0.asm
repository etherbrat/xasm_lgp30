; asm_test0.asm
; basic syntax (comment only)
; positives (comment only)
; label only (comment only)
label1:
; opcode and operand only
        b 0
; label, opcode and operand
label2: b 0
label3:        ; label and comment
        b 0    ; opcode, operand and comment
label4: b 0    ; label, opcode, operand and comment
; negatives
1abel:          ; bad label
    q 2000      ; bad opcode
    b           ; not  enough operands
    b a b       ; too many operands
    b a         ; undefined operand
    b 6000      ; bad address
    b 3000+4000 ; bad address
    b a&%       ; bad address expression
    b 3.0+4.0   ; bad address expression
    
