from xasm_lgp30.assembler_constants import *

from xasm_lgp30.expression_parserV4 import to_rpn, evaluate_rpn

from xasm_lgp30.lgp30_atq import python2atq

# See also validate_funcsV<n>.py
# Assumption: The arg(s) have been validated

def evaluate_expression(context, arg):
    try:
        rpn = to_rpn(arg)
    except Exception as problem:
        context['error_queue'].append(f"Line {context['line_number']} - {type(problem).__name__}, {str(problem)} - {arg}")
        return 0
    try:
        value = evaluate_rpn(rpn, context['symbol_table'])
        return value
    except Exception as problem:
        context['error_queue'].append(f"Line {context['line_number']} - {type(problem).__name__}, {str(problem)} - {arg}")
        return 0

def evaluate_integer(context, arg):
    value = evaluate_expression(context, arg)
    if isinstance(value, int):
        return value
    else:
        context['error_queue'].append(f"Line {context['line_number']} - Non-integer expression: {arg}")
        return 0

def evaluate_address(context, arg):
    value = evaluate_integer(context, arg)
    if MIN_ADDR <= value <= MAX_ADDR:
        return value
    else:
        context['error_queue'].append(f"Line {context['line_number']} - Illegal address value: {value}")
        return 0

def evaluate_atq(context, val_arg, q_arg):
    val_value = evaluate_expression(context, val_arg)
    q_value = evaluate_integer(context, q_arg)
    if not (MIN_Q_VALUE <= q_value <= MAX_Q_VALUE):
        context['error_queue'].append(f"Line {context['line_number']} - Illegal q value {q_arg}")
        return 0
    try:
        atq_value = python2atq(val_value, q_value)
        return atq_value
    except Exception as problem:
        context['error_queue'].append(f"Line {context['line_number']} - atq conversion error - {val_arg}, {q_arg}")
        return 0
    else:
        context['error_queue'].append(f"Line {context['line_number']} - Illegal atq value: {atq_value}")
        return 0

def evaluate_shift(context, arg):
    value = evaluate_integer(context, arg)
    if MIN_SHIFT_VALUE <= value <= MAX_SHIFT_VALUE:
        return value
    else:
        context['error_queue'].append(f"Line {context['line_number']} - Illegal shift value: {value}")
        return 0    

def evaluate_char_code(context, arg):
    value = evaluate_integer(context, arg)
    if MIN_CHAR_CODE <= value <= MAX_CHAR_CODE:
        return value
    else:
        context['error_queue'].append(f"Line {context['line_number']} - Illegal character code value: {value}")
        return 0

def evaluate_zero_char_code(context, arg):
    value = evaluate_integer(context, arg)
    if  value == 0:
        return value
    else:
        context['error_queue'].append(f"Line {context['line_number']} - Illegal character code value: {value}")
        return 0

def evaluate_character(context, arg):
    if arg in output_charset:
        return output_charset[arg][TRACK_DECIMAL_CODE]
    else:
        context['error_queue'].append(f"Line {context['line_number']} - Illegal character: {arg}")
        return 0

def evaluate_switch_mask(context, arg):
    value = evaluate_integer(context, arg)
    if (value & SW32) or (value & SW16) or (value & SW8) or (value & SW4) or (value == 0):
        return value
    else:
        context['error_queue'].append(f"Line {context['line_number']} - Illegal switch mask: {arg}")
        return 0

# returns the Friden encoding of the character
def evaluate_char(context, arg):
    return output_charset[arg][FRIDEN_DECIMAL_CODE]
