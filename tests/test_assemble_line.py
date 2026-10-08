from xasm_lgp30.assembler import assemble_line

from collections import deque # double-ended queue

import pytest

# assemble_line(input_line, context)
# context (a dictionary - everything that needs to be remembered)
# context keys:
# 'input_line'
# 'pass'
# 'radix'
# 'line_number'
# 'location_ptr'
# 'statement' (a dictionary, populated by the analyser)
#	statement keys:
#	'label'
#	'opcode'
#	'all_args'
#	'comment'
# 'updates' (a dictionary used for deferred updates to the context)
#	updates keys:
#	'pending radix'
#	'pending_locn'
#	'end_flag'
# 'error_queue' (a deque containing errors found in the current line)
# 'symbol_table' (a dictionary of symbol, value pairs)
# 'binary' (a dictionary of address, binary pairs)

def init_context(context):
    context['pass'] = 1
    context['line_number'] = 1
    context['location_ptr'] = 0
    context['statement'] = {}
    context['updates'] = {}
    context['error_queue'] = deque()
    context['binary'] = {}
    context['listing_file'] = ''

def clear_updates(context):
    context['updates']['pending_radix'] = None
    context['updates']['pending_locn'] = None
    context['updates']['end_flag'] = None

def assemble_instr(input_line):
    context = {}
    init_context(context) 
    context['symbol_table'] = {}
    _ = assemble_line(input_line, context)
    init_context(context)
    context['pass'] = 2
    _ = assemble_line(input_line, context)
    return (context['binary'][0], len(context['error_queue']), context['location_ptr'])

basic_assemble_line_tests_positive = [
    # ('instruction',(binary,len(error_queue),location_ptr))
    ('b 2000', (73536,0,1)),
    ('h 2001', (794436,0,1)),
    ('c 2002', (859976,0,1)),
    ('a 2003', (925516,0,1)),
    ('s 2004', (991056,0,1)),
    ('m 2005', (466772,0,1)),
    ('n 2006', (401240,0,1)),
    ('d 2007', (335708,0,1)),
    ('e 2008', (597856,0,1)),
    ('y 2009', (139108,0,1)),
    ('r 2010', (204648,0,1)),
    ('u 2011', (663404,0,1)),
    ('t 2012', (728944,0,1)),
    ('z 32', (8192,0,1)),
    ('p 2', (524800,0,1)),
    ('i 0', (262144,0,1)),
    ('.pchar 0', (524800,0,1)),
    ('.word 36', (36,0,1)), # an odd number would not pass - LSB set to zero
    ]
@pytest.mark.parametrize("input_line, outcome", basic_assemble_line_tests_positive)
def test_basic_assemble_instr_positive(input_line, outcome):
    assert assemble_instr(input_line) == outcome

def assemble_directive(input_line):
    context = {}
    init_context(context) 
    context['symbol_table'] = {}
    _ = assemble_line(input_line, context)
    init_context(context)
    context['pass'] = 2
    _ = assemble_line(input_line, context)
    return (context['binary'], context['symbol_table'], len(context['error_queue']), context['location_ptr'])

basic_assemble_directive_tests_positive = [
    # ('directive',({binary},{symbol table},len(error_queue),location_ptr))
    ('.locn 2013',({},{},0,2013)),
    ('.equ _symbol 2014',({},{'_symbol':2014},0,0)),
    ]
@pytest.mark.parametrize("input_line, outcome", basic_assemble_directive_tests_positive)
def test_basic_assemble_directive_positive(input_line, outcome):
    assert assemble_directive(input_line) == outcome
