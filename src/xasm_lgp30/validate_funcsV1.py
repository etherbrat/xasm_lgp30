from xasm_lgp30.assembler_constants import *

from xasm_lgp30.expression_parserV4 import is_number, is_integer, is_expression

# See also evaluate_funcsV<n>.py
# symbol validation (must be kept consistent with expression parser)
# alpha: isalpha() = True but RTFM
# numeric in 0 - 9: isdecimal() = True
# alphanumeric: isalnum() = True but RTFM

def is_symbol(context, arg):
    if re.fullmatch(SYMBOL_PATTERN, arg):
        return True
    else:
        context['error_queue'].append(f"Line {context['line_number']} - Invalid symbol: {arg}")
        return False
    
def is_label(context, arg):
    # a label is a symbol
    return is_symbol(context, arg)

def local_is_number(context, arg):
    if is_number(arg):
        return True
    else:
        context['error_queue'].append(f"Line {context['line_number']} - Invalid number: {arg}")
        return False
    
def local_is_integer(context, arg):
    if is_integer(arg):
        return True
    else:
        context['error_queue'].append(f"Line {context['line_number']} - Invalid integer: {arg}")
        return False

def local_is_expression(context, arg):
    if is_expression(arg):
        return True
    else:
        context['error_queue'].append(f"Line {context['line_number']} - Invalid expression: {arg}")
        return False

def is_integer_expression(context, arg):
    return local_is_expression(context, arg)

def is_addr_expr(context, arg):
    return local_is_expression(context, arg)

def is_word_expr(context, arg):
    return local_is_expression(context_arg)

def is_q_expr(context, arg):
    return local_is_expression(context, arg)

def is_shift_expr(context, arg):
    return local_is_expression(context, arg)

def is_char_code(context, arg):
    return local_is_expression(context, arg)

def is_zero_char_code(context, arg):
    if arg == '0':
        return True
    else:
        context['error_queue'].append(f"Line {context['line_number']} - Invalid i argument: {arg}")
        return False       

def is_character(context, arg):
    if arg in output_charset:
        return True
    else:
        context['error_queue'].append(f"Line {context['line_number']} - Invalid character: {arg}")
        return False

def is_switch_mask(context, arg):
    return is_integer_expression(context, arg)

type_dict = {
    'symbol': is_symbol, # character string in [<prefix>]<alpha>[<alphanumerics>]
    'label': is_label, # but actually, a label is a symbol
    'number': local_is_number, # parseable number
    'expression': local_is_expression, # parseable expression
    'integer_expr': is_integer_expression, # integer expression
    'addr_expr': is_addr_expr, # expression
    'word_expr': is_word_expr, # word expression
    'q_expr': is_q_expr, # q expression
    'shift_expr': is_shift_expr, # shift expression
    'char_code': is_char_code, # expression
    'zero_char_code': is_zero_char_code, # char code must be zero
    'character': is_character, # character in output character set
    'switch_mask': is_switch_mask, # switch mask
    }

def validate_args(context, dict_entry):
    args = context['statement']['all_args'].split()
    if len(args) != dict_entry[OPCODE_NUM_ARGS]:
        context['error_queue'].append(f"Line {context['line_number']} - Invalid argument count: {dict_entry[OPCODE_NUM_ARGS]} argument(s) required")
        return False
    constraint_index = 0
    for arg in args:
        if not type_dict[dict_entry[OPCODE_ARG_CONSTRAINTS][constraint_index]](context, arg):
            context['error_queue'].append(f"Line {context['line_number']} - Invalid argument: {arg}")
            return False
        constraint_index += 1
    return True

