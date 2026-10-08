from xasm_lgp30.expression_parserV4 import to_rpn, evaluate_rpn

import pytest

basic_number_tests_positive = [
    ('0', [0]),
    ('-1', [1, 'NEG']),
    ('999999', [999999]),
    ('-999999', [999999, 'NEG']),
    ('1.0', [1.0]),
    ('-1.0', [1.0, 'NEG']),
    ]
@pytest.mark.parametrize("input_data, output_data", basic_number_tests_positive)
def test_basic_numbers_positive(input_data, output_data):
    assert output_data == to_rpn(input_data)

basic_number_tests_negative = [
    ('_0', SyntaxError),
    ('0_', SyntaxError),
    ('1_5', SyntaxError),
    ('-1_5', SyntaxError),
    ('1_2_3', SyntaxError),
    ('-1_2_3', SyntaxError),
    ('999_999', SyntaxError),
    ('-999_999', SyntaxError),
    ('.1', SyntaxError),
    ('-.1', SyntaxError),   
    ]
@pytest.mark.parametrize("input_data, exception_class", basic_number_tests_negative)
def test_basic_numbers_negative(input_data, exception_class):
    with pytest.raises(exception_class):
        rpn = to_rpn(input_data)
        
basic_radix_tests_positive = [
    ('0b0', [0]),
    ('0b1', [1]),
    ('0o0', [0]),
    ('0o7', [7]),
    ('0', [0]),
    ('9', [9]),
    ('0s0', [0]),
    ('0sw', [15]),
    ('0x0', [0]),
    ('0xf', [15]),
    ('0b00000000000000000000000000000000', [0]),
    ('0b11111111111111111111111111111111', [4294967295]),
    ('0b10000000000000000000000000000000', [2147483648]),
    ('0o00000000000', [0]),
    ('0o37777777777', [4294967295]),
    ('0o20000000000', [2147483648]),
    ('0s00000000', [0]),
    ('0swwwwwwww', [4294967295]),
    ('0s80000000', [2147483648]),
    ('0x00000000', [0]),
    ('0xffffffff', [4294967295]),
    ('0x80000000', [2147483648]),
    ]
@pytest.mark.parametrize("input_data, output_data", basic_radix_tests_positive)
def test_basic_radix_positive(input_data, output_data):
    assert output_data == to_rpn(input_data)

basic_radix_tests_negative = [
    ('0b2', ValueError),
    ('0o8', ValueError),
    ('0sz', ValueError),
    ('0xg', ValueError),
    ('0b_11', SyntaxError),
    ('0b11_', SyntaxError),
    ('0b1_1', SyntaxError),
    ('0o_11', SyntaxError),
    ('0o11_', SyntaxError),
    ('0o1_1', SyntaxError),
    ('0s_11', SyntaxError),
    ('0s11_', SyntaxError),
    ('0s1_1', SyntaxError),
    ('0x_11', SyntaxError),
    ('0x11_', SyntaxError),
    ('0x1_1', SyntaxError),
    ]
@pytest.mark.parametrize("input_data, exception_class", basic_radix_tests_negative)
def test_basic_radix_negative(input_data, exception_class):
    with pytest.raises(exception_class):
        rpn = to_rpn(input_data)
        
basic_parentheses_tests_positive = [
    ('3 + 4 * 5', [3, 4, 5, '*', '+']),
    ('(3 + 4) * 5', [3, 4, '+', 5, '*']),
    ('((3 + 4) * 5) + 6 * 7', [3, 4, '+', 5, '*', 6, 7, '*', '+']),
    ('(((3 + 4) * 5) + 6) * 7', [3, 4, '+', 5, '*', 6, '+',  7, '*']),
    ('(((3 + 4) * 5) + 6) * (7 + 8)', [3, 4, '+', 5, '*', 6, '+', 7, 8, '+','*']),
    ]
@pytest.mark.parametrize("input_data, output_data", basic_parentheses_tests_positive)
def test_basic_paren_positive(input_data, output_data):
    assert output_data == to_rpn(input_data)

basic_parentheses_tests_negative = [
    ('(3 + 4 * 5', SyntaxError),
    ('3 + 4) * 5', SyntaxError),
    ('((3 + 4) * 5 + 6 * 7', SyntaxError),
    ('((3 + 4 * 5) + 6 * 7', SyntaxError),
    ('(3 + 4) * 5) + 6 * 7', SyntaxError),
    ]
@pytest.mark.parametrize("input_data, exception_class", basic_parentheses_tests_negative)
def test_basic_paren_negative(input_data, exception_class):
    with pytest.raises(exception_class):
        rpn = to_rpn(input_data)
        
basic_operator_tests_positive = [
    ('1 + 2', [1, 2, '+']),
    ('1 - 2', [1, 2, '-']),
    ('1 * 2', [1, 2, '*']),
    ('1 / 2', [1, 2, '/']),
    ('1 ** 2', [1, 2, '**']),
    ('-1', [1, 'NEG']),
    ('-1 * 2 / 3 + 4 - 5', [1, 'NEG', 2, '*', 3, '/', 4, '+', 5, '-']),
    ('1 - 2 + 3 / 4 * -5', [1, 2, '-', 3, 4, '/', 5, 'NEG', '*', '+']),
    ('- - - 1', [1, 'NEG', 'NEG', 'NEG']),
    ('---1', [1, 'NEG', 'NEG', 'NEG']),
    ]
@pytest.mark.parametrize("input_data, output_data", basic_operator_tests_positive)
def test_basic_operators_positive(input_data, output_data):
    assert output_data == to_rpn(input_data)

basic_operator_tests_negative = [
    ('1 2', SyntaxError),
    ('1 2 -', SyntaxError),
    ('1 +', SyntaxError),
    ('-', SyntaxError),
    ('1 - ', SyntaxError),
    ]
@pytest.mark.parametrize("input_data, exception_class", basic_operator_tests_negative)
def test_basic_operator_negative(input_data, exception_class):
    with pytest.raises(exception_class):
        rpn = to_rpn(input_data)

basic_function_tests_positive = [
    ('and(8, 4)', [8, 4, ('and', 2)]),
    ('or(10, 5)', [10, 5, ('or', 2)]),
    ('xor(7, 7)', [7, 7, ('xor', 2)]),
    ('not(7)', [7, ('not', 1)]),
    ('shl(10, 3)', [10, 3, ('shl', 2)]),
    ('shr(10, 3)', [10, 3, ('shr', 2)]),
    ('max(1, 2, 3, 4, 5)', [1, 2, 3, 4, 5, ('max', 5)]),
    ('max(1,2,3,4,5)', [1, 2, 3, 4, 5, ('max', 5)]),
    ('max(1,2, 3,4, 5)', [1, 2, 3, 4, 5, ('max', 5)]),
    ('shl(shl(10, 3), 4)', [10, 3, ('shl', 2), 4, ('shl', 2)]),
    ('shr(10, shl(3, 2))', [10, 3, 2, ('shl', 2), ('shr', 2)]),
    ]
@pytest.mark.parametrize("input_data, output_data", basic_function_tests_positive)
def test_basic_functions_positive(input_data, output_data):
    assert output_data == to_rpn(input_data)

basic_function_tests_negative = [
    ('shl shl(10, 3), 4)', SyntaxError),
    ('shl(shl 10, 3), 4)', SyntaxError),
    ('shl(shl(10, 3, 4)', SyntaxError),
    ('shl(shl(10, 3), 4', SyntaxError),
    ('shl(shl(10 3), 4)', SyntaxError),
    ('shl(shl(10, 3) 4)', SyntaxError),
    ]
@pytest.mark.parametrize("input_data, exception_class", basic_function_tests_negative)
def test_basic_function_negative(input_data, exception_class):
    with pytest.raises(exception_class):
        rpn = to_rpn(input_data)

basic_overflow_tests_positive = [
    ]
@pytest.mark.parametrize("input_data, output_data", basic_overflow_tests_positive)
def test_basic_overflow_positive(input_data, output_data):
    rpn = to_rpn(input_data)
    assert output_data == evaluate_rpn(rpn)
    
basic_overflow_tests_negative = [
    ]
@pytest.mark.parametrize("input_data, exception_class", basic_overflow_tests_negative)
def test_basic_overflow_negative(input_data, exception_class):
    with pytest.raises(exception_class):
        rpn = to_rpn(input_data)
        _ = evaluate_rpn(rpn)
