# set DEBUG = True in assembler_constants.py
# Try all combinations of label: opcode operand(s) ; comment

from assembler import analyse, print_analysis

context = {}
context['statement'] = {}
while True:
    context['input_line'] = input('--> ').rstrip()
    analyse(context)
    print_analysis(context)
    