from xasm_lgp30.assembler import analyse

import pytest

# def test_analyser_positive():
# 
#     context['input_line'] = 'abc: b 2000 ; comment'
#     analyse(context)
#     assert context['statement']['label'] == 'abc' and \
#         context['statement']['opcode'] == 'b' and \
#         context['statement']['all_args'] == '2000' and \
#         context['statement']['comment'] == '; comment'

basic_analyser_tests_positive = [
    ('', {'label':'', 'opcode':'', 'all_args':'', 'comment':''}),
#
    ('abc:', {'label':'abc', 'opcode':'', 'all_args':'', 'comment':''}),
    ('abc: def', {'label':'abc', 'opcode':'def', 'all_args':'', 'comment':''}),
    ('abc: def ghj', {'label':'abc', 'opcode':'def', 'all_args':'ghj', 'comment':''}),
    ('abc: def ghj klm', {'label':'abc', 'opcode':'def', 'all_args':'ghj klm', 'comment':''}),
    ('abc: def ghj klm ; comment', {'label':'abc', 'opcode':'def', 'all_args':'ghj klm', 'comment':' comment'}),
    ('abc: ; comment', {'label':'abc', 'opcode':'', 'all_args':'', 'comment':' comment'}),
    ('abc: def ; comment', {'label':'abc', 'opcode':'def', 'all_args':'', 'comment':' comment'}),
#
    ('def', {'label':'', 'opcode':'def', 'all_args':'', 'comment':''}),
    ('def ghj', {'label':'', 'opcode':'def', 'all_args':'ghj', 'comment':''}),
    ('def ghj klm', {'label':'', 'opcode':'def', 'all_args':'ghj klm', 'comment':''}),
    ('def ghj klm ; comment', {'label':'', 'opcode':'def', 'all_args':'ghj klm', 'comment':' comment'}),    
    ('def ; comment', {'label':'', 'opcode':'def', 'all_args':'', 'comment':' comment'}),    
#
    ('; comment', {'label':'', 'opcode':'', 'all_args':'', 'comment':' comment'}),    
    ]
@pytest.mark.parametrize("input_line, statement", basic_analyser_tests_positive)
def test_basic_numbers_positive(input_line, statement):
    context = {}
    context['input_line'] = input_line
    context['statement'] = {}
    analyse(context)
    assert context['statement'] == statement
