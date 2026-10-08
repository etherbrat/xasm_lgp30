from xasm_lgp30.expression_parserV4 import to_rpn, evaluate_rpn

import pytest

basic_radix_tests_positive = [
    ('0b0', 0),
    ('0b1', 1),
    ('0o0', 0),
    ('0o7', 7),
    ('0', 0),
    ('9', 9),
    ('0s0', 0),
    ('0sw', 15),
    ('0x0', 0),
    ('0xf', 15),
    ('1.5', 1.5),
    ]
@pytest.mark.parametrize("input_data, output_data", basic_radix_tests_positive)
def test_basic_radix_positive(input_data, output_data):
    assert output_data == evaluate_rpn(to_rpn(input_data))

basic_parentheses_tests_positive = [
    ('3 + 4 * 5', 23),
    ('(3 + 4) * 5', 35),
    ('((3 + 4) * 5) + 6 * 7', 77),
    ('(((3 + 4) * 5) + 6) * 7', 287),
    ('(((3 + 4) * 5) + 6) * (7 + 8)', 615),
    ]
@pytest.mark.parametrize("input_data, output_data", basic_parentheses_tests_positive)
def test_basic_paren_positive(input_data, output_data):
    assert output_data == evaluate_rpn(to_rpn(input_data))

basic_operator_tests_positive = [
    ('1 + 2', 3),
    ('1 - 2', -1),
    ('1 * 2', 2),
    ('1 / 2', 0.5),
    ('-1 // 2', -1),
    ('1 // 2', 0),
    ('3 ** 2', 9),
    ('-1', -1),
    ('-1 * 2 / 5 + 4 - 5', -1.4),
    ('1 - 2 + 3 / 4 * -5', -4.75),
    ('- - - 1', -1),
    ('---1', -1),
    ]
@pytest.mark.parametrize("input_data, output_data", basic_operator_tests_positive)
def test_basic_operators_positive(input_data, output_data):
    assert output_data == evaluate_rpn(to_rpn(input_data))

basic_function_tests_positive = [
    ('shl(10, 3)', 80),
    ('shr(10, 3)', 1),
    ('max(1, 2, 3, 4, 5)', 5),
    ('max(1,2,3,4,5)', 5),
    ('max(1,2, 3,4, 5)', 5),
    ('shl(shl(10, 3), 4)', 1280),
    ('shr(10, shl(3, 2))', 0),
    ]
@pytest.mark.parametrize("input_data, output_data", basic_function_tests_positive)
def test_basic_functions_positive(input_data, output_data):
    assert output_data == evaluate_rpn(to_rpn(input_data))
