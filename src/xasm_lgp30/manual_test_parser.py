from xasm_lgp30.expression_parserV4 import to_rpn, is_number, is_expression, evaluate_rpn

while True:
    input_val = input('--> ')
    if is_number(input_val):
        print("Number")
        continue
    if is_expression(input_val):
        print("Expression")
        continue
    print("Nothing")
