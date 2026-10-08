# To do:
# Will assemble content past the limit of real memory

from xasm_lgp30.assembler_constants import *

from xasm_lgp30.validate_funcsV1 import validate_args, is_label

from xasm_lgp30.evaluate_funcsV1 import *

from xasm_lgp30.expression_parserV4 import to_rpn, evaluate_rpn

from collections import deque # double-ended queue

import os # for os.path.basename()

import argparse # for command line processing

import sys # for sys.stdout

from pathlib import Path # for Path

from intelhex import IntelHex

# import contextlib # for nullcontext()

# print_<something>() statements are for debugging
# list_<something>() functions are for listing
# Listing logic:
# Each opcode will be "effective" in either Pass 1 or Pass 2 (or maybe both)
# Each invocation will pass, or fail due to validation or evaluation failures
# Hence 4 possible outcomes
# In the effective pass, success will result in a line number and source line listing, plus results
# In the non-effecive pass, success will result in a line_number and source line listing only
# In either pass, failure will result in a line number and source line listing plus an error message
# The error that is reported will be the first encountered (the first on the error queue)

def print_line_context(context):
    if DEBUG:
        print('\nStart-of-line context:')
        print(f"  Line number: {context['line_number']}")
        print(f"  Location: {context['location_ptr']}")

def print_analysis(context):
    if DEBUG:
        print('Analysis:')
        print(f"  Input line: {repr(context['input_line'])}")
        print(f"  Label: {repr(context['statement']['label'])}")
        print(f"  Opcode: {repr(context['statement']['opcode'])}")
        print(f"  Args: {repr(context['statement']['all_args'])}")
        print(f"  Comment: {repr(context['statement']['comment'])}")
    
def print_all_binary(context):
    if DEBUG:
        print('Output:')
        sorted_addresses = sorted(context['binary'])
        for address in sorted_addresses:
            print(f"{address}: {context['binary'][address]}")
        
def bin_to_sex(binary_value):
    # No need for lobal constants
    SEX_DIGITS_PER_WORD = 8
    NUM_GROUPS = 2
    SEX_DIGITS_PER_GROUP = int(SEX_DIGITS_PER_WORD / NUM_GROUPS)
    BITS_PER_DIGIT = 4
    DIGIT_VALUE_MASK = 15
    sex = ''
    for spacer in ('', ' '):
        sex = spacer + sex
        for i in range(SEX_DIGITS_PER_GROUP):
            # first 4-digit group
            digit_value = binary_value & DIGIT_VALUE_MASK
            binary_value = binary_value >> BITS_PER_DIGIT
            digit_char = next((digit_char for digit_char, value in sex_charset.items() if value == digit_value), None)
            sex = digit_char + sex
    return sex

def bin_2_hex(binary_value):
    # No need for lobal constants
    HEX_DIGITS_PER_WORD = 8
    NUM_GROUPS = 2
    HEX_DIGITS_PER_GROUP = int(HEX_DIGITS_PER_WORD / NUM_GROUPS)
    BITS_PER_DIGIT = 4
    DIGIT_VALUE_MASK = 15
    hexstr = ''
    for spacer in ('', ' '):
        hexstr = spacer + hexstr
        for i in range(HEX_DIGITS_PER_GROUP):
            # first 4-digit group
            digit_value = binary_value & DIGIT_VALUE_MASK
            binary_value = binary_value >> BITS_PER_DIGIT
            digit_char = f"{digit_value:0x}"
            hexstr = digit_char + hexstr
    return hexstr

def print_binary(context):
    if DEBUG:
        binary = context['binary'][context['location_ptr']]
        opcode_value = (binary & ASM_OPCODE_MASK) >> ASM_OPCODE_SHIFT
        address_value = (binary & ASM_ADDRESS_MASK) >> ASM_ADDRESS_SHIFT
        track_value = (binary & ASM_TRACK_MASK) >> ASM_TRACK_SHIFT
        sector_value = address_value - track_value * (MAX_SECTOR + 1)
        print('Output:')
        print(f"  Location ptr: {context['location_ptr']}")
        print(f"  Opcode value: {opcode_value}")
        print(f"  Address: {address_value}")
        print(f"  Track: {track_value}")
        print(f"  Sector: {sector_value}")
        print(f"  Binary: {binary}")
        print(f"  Sexadecimal: {bin_to_sex(binary)}")
  
def print_pending_locn(context):
    if DEBUG:
        print(f"Pending location ptr: {context['updates']['pending_locn']}")
    
def print_symbol_and_value(context):
    if DEBUG:
        arg_list = context['statement']['all_args'].split()
        symbol_arg = arg_list[0]
        print(f"Symbol: {symbol_arg} = {context['symbol_table'][symbol_arg]}")
    
def print_label_and_value(context):
    if DEBUG:
        print(f"Label: {context['statement']['label']} = {context['symbol_table'][context['statement']['label']]}")
    
def print_word(context):
    if DEBUG:
        binary = context['binary'][context['location_ptr']]
        print('Output:')
        print(f"  Location ptr: {context['location_ptr']}")
        print(f"  Binary:  {binary}")
        print(f"  Sexadecimal: {bin_to_sex(binary)}")

def print_start_address(context):
    if DEBUG:
        print(f"Start_address: {context['start_address']}")

def print_error_queue(context):
    if DEBUG:
        print('Error queue:')
        for element in context['error_queue']:
            print(f"  {element}")

def print_updates(context):
    if DEBUG:
        print('Updates:')
        print(f"  pending_locn: {context['updates']['pending_locn']}")
        print(f"  end_flag: {context['updates']['end_flag']}")

def console_end_of_pass_msg(context):
    print(f"End of pass {context['pass']} - {context['pass_error_count']} errors")

def expand_line(context):
    return (f"{context['input_line'].expandtabs(LISTING_TAB_INTERVAL):<40.40} ")

def list_line_only(context):
    if context['listing_file']:
        print(f"{context['line_number']:4} ", file=context['listing_file'], end='')
        print(expand_line(context), file=context['listing_file'], end='')
        print(file=context['listing_file'])

def list_line_and_error(context):
    if context['listing_file']:
        print(f"{context['line_number']:4} ", file=context['listing_file'], end='')
        print(expand_line(context), file=context['listing_file'], end='')
        print(f"Error: {context['error_queue'][0]}", file=context['listing_file'])        
  
def list_line_and_binary(context):
    if context['listing_file']:
        binary = context['binary'][context['location_ptr']]
        opcode_value = (binary & ASM_OPCODE_MASK) >> ASM_OPCODE_SHIFT
        address_value = (binary & ASM_ADDRESS_MASK) >> ASM_ADDRESS_SHIFT
        track_value = (binary & ASM_TRACK_MASK) >> ASM_TRACK_SHIFT
        sector_value = address_value - track_value * (MAX_SECTOR + 1)
        print(f"{context['line_number']:4} ", file=context['listing_file'], end='')
        print(expand_line(context), file=context['listing_file'], end='')
        print(f"{context['location_ptr']:4} ", file=context['listing_file'], end='')
        print(f"{context['statement']['opcode']:6} ", file=context['listing_file'], end='')
        print(f"{address_value:4} ", file=context['listing_file'], end='')
        print(f"{track_value:2} ", file=context['listing_file'], end='')
        print(f"{sector_value:2} ", file=context['listing_file'], end='')
        print(f"{binary:12} ", file=context['listing_file'], end='')
        print(f"{bin_to_sex(binary):8} ", file=context['listing_file'], end='')
        if LIST_HEX:
            print(f"{bin_2_hex(binary):8}", file=context['listing_file'])
        else:
            print(file=context['listing_file'])
  
def list_line_and_pending_locn(context):
    if context['listing_file']:
        print(f"{context['line_number']:4} ", file=context['listing_file'], end='')
        print(expand_line(context), file=context['listing_file'], end='')
        print(f"locn = {context['updates']['pending_locn']:4}", file=context['listing_file'])
    
def list_line_and_symbol_and_value(context):
    if context['listing_file']:
        arg_list = context['statement']['all_args'].split()
        symbol_arg = arg_list[0]
        print(f"{context['line_number']:4} ", file=context['listing_file'], end='')
        print(expand_line(context), file=context['listing_file'], end='')
        print(f"{symbol_arg} = {context['symbol_table'][symbol_arg]}", file=context['listing_file'])
    
def list_line_and_label_and_value(context):
    if context['listing_file']:
        label = context['statement']['label']
        print(f"{context['line_number']:4} ", file=context['listing_file'], end='')
        print(expand_line(context), file=context['listing_file'], end='')
        print(f"{label} = {context['symbol_table'][label]}", file=context['listing_file'])
    
def list_line_and_word(context):
    if context['listing_file']:
        binary = context['binary'][context['location_ptr']]
        print(f"{context['line_number']:4} ", file=context['listing_file'], end='')
        print(expand_line(context), file=context['listing_file'], end='')
        print(f"{context['location_ptr']:4} ", file=context['listing_file'], end='')
        print(f"{'':<17} ", file=context['listing_file'], end='')
        print(f"{binary:12} ", file=context['listing_file'], end='')
        print(f"{bin_to_sex(binary):8} ", file=context['listing_file'], end='')
        if LIST_HEX:
            print(f"{bin_2_hex(binary):8}", file=context['listing_file'])
        else:
            print(file=context['listing_file'])

def list_line_and_start_address(context):
    if context['listing_file']:
        print(f"{context['line_number']:4} ", file=context['listing_file'], end='')
        print(expand_line(context), file=context['listing_file'], end='')
        print(f"Start: {context['start_address']}", file=context['listing_file'])

def list_symbol_table(context):
    if context['listing_file']:
        print('\nSymbol Table:', file=context['listing_file'])
        print('------ ------', file=context['listing_file'])
        for symbol in context['symbol_table']:
            print(f"{symbol:12} : {context['symbol_table'][symbol]:12}", file=context['listing_file'])
            
def clear_updates(context):
    context['updates']['pending_locn'] = None
    context['updates']['end_flag'] = None

def set_pending_locn(context, value):
    context['updates']['pending_locn'] = value

def set_end_flag(context):
    context['updates']['end_flag'] = 'end'

def new_symbol(context, symbol_arg, value_arg):
    if symbol_arg in context['symbol_table']:
        context['error_queue'].append(f"Line {context['line_number']} - Multiply defined symbol: {symbol_arg}")
        return False
    else:
        value = evaluate_expression(context, value_arg)
        context['symbol_table'][symbol_arg] = value
        return True

def assemble_memory_instr(opcode_value, operand_value):
    return (opcode_value<<ASM_OPCODE_SHIFT) + (operand_value<<ASM_ADDRESS_SHIFT)

def assemble_track_instr(opcode_value, address_value):
    return (opcode_value<<ASM_OPCODE_SHIFT) + (address_value<<ASM_TRACK_SHIFT)

def opcode_mem_operand(context, dict_entry): # opcodes with memory address operands 
    set_pending_locn(context, context['location_ptr'] + 1)
    if context['pass'] == 1:
        # Validate args
        if validate_args(context, dict_entry):
            list_line_only(context)
            return
        else:
            list_line_and_error(context)
            return
    # Keep the two passes separate for clarity
    elif context['pass'] == 2:
        # Re-validate args
        if validate_args(context, dict_entry):
            # Assembly happens here
            # Look up the opcode
            # Evaluate the arg (if necessary and possible)
            # Assemble binary from opcode value and arg value
            # Add binary to context
            opcode_value = opcode_dict[context['statement']['opcode']][OPCODE_VAL]
            address_arg = context['statement']['all_args'].split()[0]
            address_value = evaluate_address(context, address_arg)
            if len(context['error_queue']) == 0:
                instruction_binary = assemble_memory_instr(opcode_value, address_value)
                context['binary'][context['location_ptr']] = instruction_binary
                print_binary(context)
                list_line_and_binary(context)
                return
            else:
                list_line_and_error(context)
                return
        else:
            list_line_and_error(context)
            return
    else:
        context['error_queue'].append(f"Line {context['line_number']} - Invalid pass number: {context['pass']}")
        return

def opcode_z(context, dict_entry):
    # in this case, the argument is a switch mask, destined for the track field
    set_pending_locn(context, context['location_ptr'] + 1)
    if context['pass'] == 1:       
        # Validate args
        if validate_args(context, dict_entry):
            list_line_only(context)
            return
        else:
            list_line_and_error(context)
            return
    # Keep the two passes separate for clarity
    elif context['pass'] == 2:
        # Re-validate args
        if validate_args(context, dict_entry):
            # Assembly happens here
            # Look up the opcode
            # Evaluate the arg (if necessary and possible)
            # Assemble binary from opcode value and arg value
            # Add binary to context
            opcode_value = opcode_dict[context['statement']['opcode']][OPCODE_VAL]
            switch_mask_arg = context['statement']['all_args'].split()[0]
            switch_mask = evaluate_switch_mask(context, switch_mask_arg)
            if len(context['error_queue']) == 0:
                instruction_binary = assemble_track_instr(opcode_value, switch_mask)
                context['binary'][context['location_ptr']] = instruction_binary
                print_binary(context)
                list_line_and_binary(context)
                return
            else:
                list_line_and_error(context)
                return
        else:
            list_line_and_error(context)
            return
    else:
        context['error_queue'].append(f"Line {context['line_number']} - Invalid pass number: {context['pass']}")
        return


def opcode_p(context, dict_entry):
    # in this case, the arg is a character code, destined for the track field
    set_pending_locn(context, context['location_ptr'] + 1)
    if context['pass'] == 1:       
        # Validate args
        if validate_args(context, dict_entry):
            list_line_only(context)
            return
        else:
            list_line_and_error(context)
            return
    # Keep the two passes separate for clarity
    elif context['pass'] == 2:
        # Re-validate args
        if validate_args(context, dict_entry):
            # Assembly happens here
            # Look up the opcode
            # Evaluate the arg (if necessary and possible)
            # Assemble binary from opcode value and arg value
            # Add binary to context
            opcode_value = opcode_dict[context['statement']['opcode']][OPCODE_VAL]
            character_code_arg = context['statement']['all_args'].split()[0]
            character_code = evaluate_char_code(context, character_code_arg)
            if len(context['error_queue']) == 0:
                instruction_binary = assemble_track_instr(opcode_value, character_code)
                context['binary'][context['location_ptr']] = instruction_binary
                print_binary(context)
                list_line_and_binary(context)
                return
            else:
                list_line_and_error(context)
                return
        else:
            list_line_and_error(context)
            return
    else:
        context['error_queue'].append(f"Line {context['line_number']} - Invalid pass number: {context['pass']}")
        return

def opcode_i(context, dict_entry):
    # in this case, the arg must be zero, destined for the track field
    set_pending_locn(context, context['location_ptr'] + 1)
    if context['pass'] == 1:       
        # Validate args
        if validate_args(context, dict_entry):
            list_line_only(context)
            return
        else:
            list_line_and_error(context)
            return
    # Keep the two passes separate for clarity
    elif context['pass'] == 2:
        # Re-validate args
        if validate_args(context, dict_entry):
            # Assembly happens here
            # Look up the opcode
            # Evaluate the arg (if necessary and possible)
            # Assemble binary from opcode value and arg value
            # Add binary to context
            opcode_value = opcode_dict[context['statement']['opcode']][OPCODE_VAL]
            character_code_arg = context['statement']['all_args'].split()[0]
            character_code = evaluate_zero_char_code(context, character_code_arg)
            if len(context['error_queue']) == 0:
                instruction_binary = assemble_track_instr(opcode_value, character_code)
                context['binary'][context['location_ptr']] = instruction_binary
                print_binary(context)
                list_line_and_binary(context)
                return
            else:
                list_line_and_error(context)
                return            
        else:
            list_line_and_error(context)
            return
    else:
        context['error_queue'].append(f"Line {context['line_number']} - Invalid pass number: {context['pass']}")
        return

def opcode_locn(context, dict_entry): # set location
    if context['pass'] in (1, 2):
        if validate_args(context, dict_entry):
            # Assembly happens here
            # Look up the opcode
            # Evaluate the arg (if necessary and possible)
            # Assemble binary from opcode value and arg value
            # Add binary to context
            address_arg = context['statement']['all_args'].split()[0]
            address_value = evaluate_address(context, address_arg)
            if len(context['error_queue']) == 0:
                context['updates']['pending_locn'] = address_value
                print_pending_locn(context)
                list_line_and_pending_locn(context)
                return
            else:
                list_line_and_error(context)
                return
        else:
            list_line_and_error(context)
            return
    else:
        context['error_queue'].append(f"Invalid pass number: {context['pass']}")
        return

def opcode_equ(context, dict_entry): # set symbol to value
    if context['pass'] == 1:
        # Validate args
        if validate_args(context, dict_entry):
            # Assembly happens here
            # Look up the opcode
            # Evaluate the arg (if necessary and possible)
            # Assemble binary from opcode value and arg value
            # Add binary to context
            arg_list = context['statement']['all_args'].split()
            symbol_arg = arg_list[0]
            value_arg = arg_list[1]
            new_symbol(context, symbol_arg, value_arg)
            if len(context['error_queue']) == 0:            
                print_symbol_and_value(context)
                list_line_and_symbol_and_value(context)
                return
            else:
                list_line_and_error(context)
                return
        else:
            list_line_and_error(context)
            return
    elif context['pass'] == 2:
        pass
    else:
        context['error_queue'].append(f"Line {context['line_number']} - Invalid pass number: {context['pass']}")
        return

def opcode_word(context, dict_entry): # assemble word
    set_pending_locn(context, context['location_ptr'] + 1)
    if context['pass'] == 1:
        # Validate args
        if validate_args(context, dict_entry):
            list_line_only(context)
            return
        else:
            list_line_and_error(context)
            return
    # Keep the two passes separate for clarity
    elif context['pass'] == 2:
        # Re-validate args
        if validate_args(context, dict_entry):
            # Assembly happens here
            # Evaluate the arg (if necessary and possible)
            # Assemble binary from arg value
            # Add binary to context
            value_arg = context['statement']['all_args'].split()[0]
            value = evaluate_integer(context, value_arg)
            # Chop negative values to 31-bits and zero the LSB
            if len(context['error_queue']) == 0:            
                value = value & WORD_MASK
                context['binary'][context['location_ptr']] = value
                print_word(context)
                list_line_and_word(context)
                return
            else:
                list_line_and_error(context)
                return
        else:
            list_line_and_error(context)
            return
    else:
        context['error_queue'].append(f"Line {context['line_number']} - Invalid pass number: {context['pass']}")
        return

def opcode_blkw(context, dict_entry): # assemble block of words
    if context['pass'] == 1:
        # Validate args
        if validate_args(context, dict_entry):
            args = context['statement']['all_args'].split()
            num_locations_arg = args[0]
            num_locations = evaluate_integer(context, num_locations_arg)
            if len(context['error_queue']) == 0:
                set_pending_locn(context, context['location_ptr'] + num_locations)
                list_line_only(context)
                return
            else:
                list_line_and_error(context)
                return
        else:
            list_line_and_error(context)
            return
    # Keep the two passes separate for clarity
    elif context['pass'] == 2:
        # Re-validate args
        if validate_args(context, dict_entry):
            # Assembly happens here
            # Evaluate the args (if necessary and possible)
            # Assemble binary from arg value
            # Add binary to context
            args = context['statement']['all_args'].split()
            num_locations_arg = args[0]
            num_locations = evaluate_integer(context, num_locations_arg)
            if len(context['error_queue']) == 0:
                for _ in range(num_locations):
                    context['binary'][context['location_ptr']] = 0
                    context['location_ptr'] += 1
                    set_pending_locn(context, context['location_ptr'])
                    print_word(context)
                list_line_only(context)
                return
            else:
                list_line_and_error(context)
                return
        else:
            list_line_and_error(context)
            return
    else:
        context['error_queue'].append(f"Line {context['line_number']} - Invalid pass number: {context['pass']}")
        return
    
def opcode_atq(context, dict_entry): # assemble word at q value
    set_pending_locn(context, context['location_ptr'] + 1)
    if context['pass'] == 1:
        # Validate args
        if validate_args(context, dict_entry):
            list_line_only(context)
            return
        else:
            list_line_and_error(context)
            return
    # Keep the two passes separate for clarity
    elif context['pass'] == 2:
        # Re-validate args
        if validate_args(context, dict_entry):
            # Assembly happens here
            # Evaluate the arg (if necessary and possible)
            # Assemble binary from arg value
            # Add binary to context
            args = context['statement']['all_args'].split()
            value_arg = args[0]
            q_arg = args[1]
            value = evaluate_atq(context, value_arg, q_arg)
            if len(context['error_queue']) == 0:
                context['binary'][context['location_ptr']] = value
                print_word(context)
                list_line_and_word(context)
                return
            else:
                list_line_and_error(context)
                return      
        else:
            list_line_and_error(context)
            return
    else:
        context['error_queue'].append(f"Line {context['line_number']} - Invalid pass number: {context['pass']}")
        return

def opcode_lshn(context, dict_entry): # assemble word for left shift by n multiply
    set_pending_locn(context, context['location_ptr'] + 1)
    if context['pass'] == 1:
        # Validate args
        if validate_args(context, dict_entry):
            list_line_only(context)
            return
        else:
            list_line_and_error(context)
            return
    # Keep the two passes separate for clarity
    elif context['pass'] == 2:
        # Re-validate args
        if validate_args(context, dict_entry):
            # Assembly happens here
            # Evaluate the arg (if necessary and possible)
            # Assemble binary from arg value
            # Add binary to context
            shift_arg = context['statement']['all_args'].split()[0]
            shift = evaluate_shift(context, shift_arg)
            if len(context['error_queue']) == 0:
                context['binary'][context['location_ptr']] = 2**(shift)
                print_word(context)
                list_line_and_word(context)
                return
            else:
                list_line_and_error(context)
                return
        else:
            list_line_and_error(context)
            return
    else:
        context['error_queue'].append(f"Line {context['line_number']} - Invalid pass number: {context['pass']}")
        return

def opcode_rshm(context, dict_entry): # assemble word for right shift by m multiply
    set_pending_locn(context, context['location_ptr'] + 1)
    if context['pass'] == 1:
        # Validate args
        if validate_args(context, dict_entry):
            list_line_only(context)
            return
        else:
            list_line_and_error(context)
            return
    # Keep the two passes separate for clarity
    elif context['pass'] == 2:
        # Re-validate args
        if validate_args(context, dict_entry):
            # Assembly happens here
            # Evaluate the arg (if necessary and possible)
            # Assemble binary from arg value
            # Add binary to context
            shift_arg = context['statement']['all_args'].split()[0]
            shift = evaluate_shift(context, shift_arg)
            if len(context['error_queue']) == 0:
                context['binary'][context['location_ptr']] = 2**(31-shift)
                print_word(context)
                list_line_and_word(context)
                return
            else:
                list_line_and_error(context)
                return
        else:
            list_line_and_error(context)
            return
    else:
        context['error_queue'].append(f"Line {context['line_number']} - Invalid pass number: {context['pass']}")
        return

def opcode_pchar(context, dict_entry): # asemble a p instr to print a character
    set_pending_locn(context, context['location_ptr'] + 1)
    if context['pass'] == 1:
        # Validate args
        if validate_args(context, dict_entry):
            list_line_only(context)
            return
        else:
            list_line_and_error(context)
            return
    # Keep the two passes separate for clarity
    elif context['pass'] == 2:
        # Re-validate args
        if validate_args(context, dict_entry):
            # Assembly happens here
            # Look up the opcode
            # Evaluate the arg (if necessary and possible)
            # Assemble binary from opcode value and arg value
            # Add binary to context
            opcode_value = opcode_dict[context['statement']['opcode']][OPCODE_VAL]
            char_arg = context['statement']['all_args'].split()[0]
            track_value = output_charset[char_arg][TRACK_DECIMAL_CODE]
            if len(context['error_queue']) == 0:
                instruction_binary = assemble_track_instr(opcode_value, track_value)
                context['binary'][context['location_ptr']] = instruction_binary
                print_binary(context)
                list_line_and_binary(context)
                return
            else:
                list_line_and_error(context)
                return
        else:
            list_line_and_error(context)
            return
    else:
        context['error_queue'].append(f"Line {context['line_number']} - Invalid pass number: {context['pass']}")
        return

def opcode_end(context, dict_entry): # stop assembling
    if context['pass'] == 1:
        # Validate args
        if validate_args(context, dict_entry):
            set_end_flag(context)
            list_line_only(context)
            return
        else:
            list_line_and_error(context)
            return
    # Keep the two passes separate for clarity
    elif context['pass'] == 2:
        # Re-validate args
        if validate_args(context, dict_entry):
            # Assembly happens here
            # Evaluate the arg (if necessary and possible)
            set_end_flag(context)
            address_arg = context['statement']['all_args'].split()[0]
            address_value = evaluate_address(context, address_arg)
            if len(context['error_queue']) == 0:
                context['start_address'] = address_value
                print_start_address(context)
                list_line_and_start_address(context)
                return
            else:
                list_line_and_error(context)
                return
        else:
            list_line_and_error(context)
            return
    else:
        context['error_queue'].append(f"Line {context['line_number']} - Invalid pass number: {context['pass']}")
        return

# Statement analyser:
# We require that the line has been stripped of all leading and trailing whitespace
# Everything before the first colon is the label
# Everything after the first semicolon is the comment
# Of the remainder, substrings are split by whitespace
# The first substring is the opcode
# The remaining substrings are re-joined by spaces to form all_args
def analyse(context):
    work_string = context['input_line']
    # everything after the first semicolon is the comment
    semicolon_pos = work_string.find(';')
    if semicolon_pos >=0:
        context['statement']['comment'] = work_string[semicolon_pos+1:]
        work_string = work_string[:semicolon_pos]
        # the comment has been dropped
    else:
        context['statement']['comment'] = ''    
    # everything before the first non-comment colon is the (unvalidated) label
    colon_pos = work_string.find(':')
    if colon_pos >= 0:
        context['statement']['label'] = work_string[:colon_pos]
        work_string = work_string[colon_pos+1:]
        # the label has been dropped
    else:
        context['statement']['label'] = ''
    segments = work_string.split()
    if len(segments) >= 1:
        context['statement']['opcode'] = segments[0]
        del segments[0]
        # the opcode has been dropped
        # what's left is all_args
        context['statement']['all_args'] = ' '.join(segments)
    else:
        context['statement']['opcode'] = ''
        context['statement']['all_args'] = ''
    return    

opcode_dict = {
    'b':('b', 1, ['addr_expr'], opcode_mem_operand, 1), # bring
    'h':('h', 1, ['addr_expr'], opcode_mem_operand, 12), # store and hold
    'c':('c', 1, ['addr_expr'], opcode_mem_operand, 13), # store and clear
    'a':('a', 1, ['addr_expr'], opcode_mem_operand, 14), # add
    's':('s', 1, ['addr_expr'], opcode_mem_operand, 15), # subtract
    'm':('m', 1, ['addr_expr'], opcode_mem_operand, 7), # multiply upper
    'n':('n', 1, ['addr_expr'], opcode_mem_operand, 6), # multiply lower
    'd':('d', 1, ['addr_expr'], opcode_mem_operand, 5), # divide
    'e':('e', 1, ['addr_expr'], opcode_mem_operand, 9), # extract
    'y':('y', 1, ['addr_expr'], opcode_mem_operand, 2), # store address
    'r':('r', 1, ['addr_expr'], opcode_mem_operand, 3), # return address
    'u':('u', 1, ['addr_expr'], opcode_mem_operand, 10), # unconditional transfer
    't':('t', 1, ['addr_expr'], opcode_mem_operand, 11), # test
    'z':('z', 1, ['switch_mask'], opcode_z, 0), # stop
    'p':('p', 1, ['char_code'], opcode_p, 8), # print code
    'i':('i', 1, ['zero_char_code'], opcode_i, 4), # input
    '.locn':('.locn', 1, ['addr_expr'], opcode_locn, 0), # set location pointer to value
    '.equ':('.equ', 2, ['symbol', 'expression'], opcode_equ, 0), # set symbol to value       
    '.word':('.word', 1, ['integer_expr'], opcode_word, 0), # set word to value
    '.blkw':('.blkw', 1, ['integer_expr'], opcode_blkw, 0), # set words to value
    '.atq': ('.atq', 2, ['expression', 'q_expr'], opcode_atq, 0), # set word to value at q value
    '.lshn':('.lshn', 1, ['shift_expr'], opcode_lshn, 0), # set word for left shift by n multiply
    '.rshm':('.rshm', 1, ['shift_expr'], opcode_rshm, 0), # set word for right shift by m multiply
    '.pchar':('.pchar', 1, ['character'], opcode_pchar, 8), # print character - use opcode value for p       
    '.end':('.end', 1, ['addr_expr'], opcode_end, 0) # stop assembling       
    }

def assemble_line(input_line, context):
    # per line initialisation
    # We .rstrip() only, to remove newlines, etc.,
    # but preserve user formatting on the left.
    # With luck, .split() gives us clean elements.
    context['input_line'] = input_line.rstrip()
    context['statement'] = {}
    clear_updates(context)
    context['error_queue'].clear()

    # carve line into elements
    analyse(context)
    print_analysis(context)
    
    # deal with the label (if any)
    if context['statement']['label']:
        # unvalidated label text found
        if is_label(context, context['statement']['label']):
            if context['pass'] == 1:
            # the symbol table is built in pass 1
                if new_symbol(context, context['statement']['label'], str(context['location_ptr'])):
                    # all good
                    pass
                else:
                    context['error_queue'].append(f"Line {context['line_number']} - Cannot create label: {context['statement']['label']}")
                    list_line_and_error(context)
        else:
            context['error_queue'].append(f"Line {context['line_number']} - Invalid label: {context['statement']['label']}")
            list_line_and_error(context)
    else:
        # no label text found
        pass

    if len(context['error_queue']) == 0:
        # deal with the other elements (if any)
        if not (context['statement']['opcode']):
            # a statement with no opcode is valid (it will also have no arguments)
            list_line_only(context)
        else:
            # a statement with an opcode must have a valid opcode and matching arguments
            if (context['statement']['opcode'].lower() not in opcode_dict):
                context['error_queue'].append(f"Line {context['line_number']} - Invalid opcode: {context['statement']['opcode']}")
                list_line_and_error(context)
            else:
                # dict_entry is the opcode_dict entry for this opcode
                dict_entry = opcode_dict[context['statement']['opcode'].lower()]
                # dict_entry[OPCODE_PROCESSOR] is the opcode-specific processor
                dict_entry[OPCODE_PROCESSOR](context, dict_entry)

    # the washup
    if len(context['error_queue']) != 0:
        context['pass_error_count'] += 1
    print_error_queue(context)
    print_updates(context)
    if context['updates']['pending_locn']:
        context['location_ptr'] = context['updates']['pending_locn']
    if context['updates']['end_flag'] == 'end':
        return 'end'
    else:
        return ''
    
def assemble_pass(source_file_path, context):
    # pass 1 validates arguments and builds the symbol table
    # pass 2 re-validates arguments and produces the binary

    # context (a dictionary - everything that needs to be remembered)
    # context keys:
    # 'input_line'
    # 'pass'
    # 'line_number'
    # 'location_ptr'
    # 'statement' (a dictionary, populated by the analyser)
    #  statement keys:
    #   'label'
    #   'opcode'
    #   'all_args'
    #   'comment'
    # 'updates' (a dictionary used for deferred updates to the context)
    #   updates keys:
    #   'pending_locn'
    #   'end_flag'
    # 'error_queue' (errors found in the current line)
    # 'pass_error_count' (count of errors in pass)
    # 'symbol_table' (a dictionary of symbol, value pairs)
    # 'binary' (a dictionary of address, binary pairs)
    # 'listing_file' (a file handle for the listing)

    # per pass initialisation
    context['line_number'] = 1
    context['location_ptr'] = DEFAULT_LOCATION_PTR # expect this to be changed with ".locn <address>"
    context['pass_error_count'] = 0

    if context['listing_file']:
        print(f"\nPass {context['pass']}", file=context['listing_file'])
        print(f"{'Line':>4} {'Statement':40} {'Locn':>4} {'Opcode'} {'Addr':>4} {'T':>2} {'S':>2} {'Dec':>12} {'Sex':9} ", end='', file=context['listing_file'])
        if LIST_HEX:
            print(f"{'Hex':9}", file=context['listing_file'])
        else:
            print(file=context['listing_file'])
        print(f"{'----':>4} {'---------':40} {'----':>4} {'------'} {'----':>4} {'-':>2} {'-':>2} {'---':>12} {'---':9} ", end ='', file=context['listing_file'])
        if LIST_HEX:
            print(f"{'---':9}", file=context['listing_file'])
        else:
            print(file=context['listing_file'])
    with open(source_file_path, 'r', encoding='utf-8') as f_source:
#    with contextlib.nullcontext():
        for input_line in f_source:
#        while True:
            print_line_context(context)
#            input_line = input('--> ')
            if assemble_line(input_line, context) == 'end':
                break
            context['line_number'] += 1
        f_source.close()
        console_end_of_pass_msg(context)
        list_symbol_table(context)
        return
    
def words_to_bytes(binary_words):
    binary_bytes = {}
    for enumerator, (address, data) in enumerate(binary_words.items()):
        byte_list = []
        for index in range(HEX_PER_WORD):
            byte_list.append(data & HEX_MASK)
            data = data >> (BITS_PER_HEX)
        # big endian
        byte_list.reverse()
        for index, byte in enumerate(byte_list):
            binary_bytes[address*HEX_PER_WORD + index] = byte
    return binary_bytes

def bytes_to_intel_hex(binary_bytes, start_address, filename):
    ih = IntelHex(binary_bytes)
    ih.start_addr = {'CS':0, 'IP':start_address}
    ih.tofile(filename, format='hex', byte_count=BYTES_PER_HEX_RECORD)

def assemble_main(source_file_path, object_file_path, listing_file_path):
    # build the skeleton of the context
    # elements are initialised as required per pass and per line
    context = {}
    context['updates'] = {}
    context['error_queue'] = deque()
    context['symbol_table'] = {}
    context['binary'] = {}
    if listing_file_path:
        try:
            context['listing_file'] = open(listing_file_path, 'w', encoding='utf-8')
            print(f"Listing file: {listing_file_path}")
        except:
            print('Error: Could not open listing file')
            context['listing_file'] = sys.stdout # revert to console
    else:
        context['listing_file'] = sys.stdout
        
    test_path = Path(source_file_path)
    if test_path.is_file():
        # assemble
        print(f"Source file: {source_file_path}")
        for context['pass'] in (1, 2):
            assemble_pass(source_file_path, context)
        print_all_binary(context)
        # optionally output the binary
        if object_file_path:
            print(f"Object file: {object_file_path}")
            if 'start_address' not in context.keys():
                print(f'Warning: Start address not specified - set to 0')
                context['start_address'] = 0
            bytes_to_intel_hex(words_to_bytes(context['binary']), context['start_address'], object_file_path)
        # tidy up
        if listing_file_path:
            try:
                context['listing_file'].close()
            except:
                pass
    else:
        print(f"Error: Input file not found {source_file_path}")

def main():
    
    print(f"XASM_LGP30 Version {XASM_LGP30_VERSION}")
    cmdline_parser = argparse.ArgumentParser()
    # positional argument (arg1)
    cmdline_parser.add_argument("source_file_path")
    # optional argument (-o arg2)
    cmdline_parser.add_argument("-o", dest="object_file_path")
    # optional argument (-o arg3)
    cmdline_parser.add_argument("-l", dest="listing_file_path")
    try:
        args = cmdline_parser.parse_args()
    except:
        print('Command line could not be parsed')
        print('Usage (.exe version): assembler source_file_path -o object_file_path -l listing_file_path')
        return

    assemble_main(args.source_file_path, args.object_file_path, args.listing_file_path)
    
if __name__ == '__main__':
    main()
    