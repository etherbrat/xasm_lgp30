# Written by ChatGPT in February 2026.

# Modified by Neil Higgins in June 2026:
# LGP-30 support added.
# The converters take unsigned literals - negation is
# normally handled by the evaluator.
# Literals are integer only - floats are not supported.
# Unprefixed numbers are always decimal.
# Prefixes are 0b (binary), 0o(octal), 0x (hexadecimal),
# and 0s (LGP-30 sexadecimal).
# Binary, octal, hex and sex literals are converted to
# native Python integers, i.e. the bit pattern is unchanged
# but they will subsequently be rendered as signed integers.
# Parser raises:
# ValueError - Invalid sexadecimal digit
# ValueError - Invalid radix
# ValueError - Illegal digit in numeric literal
# SyntaxError - Illegal character
# SyntaxError - Unexpected type
# SyntaxError - Unexpected token after expression
# SyntaxError - Unexpected token
# Exceptions added:
# Value error - 0b, 0o, 0x or 0s literal exceeds 31 bits
# Evaluator raises:
# ValueError - Unknown function
# ValueError - Unknown RPN token
# ValueError - Invalid RPN expression
# Exceptions added:
# Value error - 31-bit twos compliment overflow

# Modified by Neil Higgins in July 2026:
# Re-admit floating point numbers for use in .atq directive.

import re

LGP30_SIGN_MASK = 0x80000000
LGP30_WORD_MASK = 0xfffffffe
LGP30_MININT = -1073741824
LGP30_MAXINT = 1073741823

# -------------------------------
# Converters for numeric literals
# -------------------------------
SEX_DIGITS = "0123456789fgjkqwFGJKQW"

def convert_sexadecimal(digits):
    digits = digits.lower()
    mapping = {d: i for i, d in enumerate(SEX_DIGITS)}
    value = 0
    for d in digits:
        if d not in mapping:
            # Not reachable due to character check in caller
            raise ValueError(f"Invalid sexadecimal digit: {d}")
        value = value * 16 + mapping[d]
    return value

def convert_number(text, radix):
    # for unprefixed numbers, radix has been set to 'd' 
    # for prefixed numbers the prefix has been reduced to radix
    base_map = {
        'b': (2, "01"),
        'o': (8, "01234567"),
        'd': (10, ".0123456789"),
        'x': (16, "0123456789abcdefABCDEF"),
        's': (16, SEX_DIGITS)
    }
    if radix not in base_map:
        raise ValueError(f"Invalid radix '{radix}'")
    base, allowed = base_map[radix]
    for digit in text:
        if digit not in allowed:
            raise ValueError(f"Illegal character '{digit}' in base {base} literal")
    if radix == 's':
        value = convert_sexadecimal(text)
    else:
        if '.' in text:
            value = float(text)
        else:
            value = int(text, base)
    return value

# ---------
# Tokenizer
# ---------
# Note regex-related ordering, e.g. ** must preceded *, // must precede /
# and in general the longer regexes should precede the shorter regexes
TOKEN_SPEC = [
    ("PREFIXED", r"0[boxs][0-9A-Za-z]+"),
    ("NUMBER",   r"\d+(\.\d+)?"),
    ("IDENT",    r"_?[A-Za-z][A-Za-z0-9_]*"),
    ("POW",      r"\*\*"),
    ("IDIV",     r"//"),
    ("MUL",      r"\*"),
    ("DIV",      r"/"),
    ("PLUS",     r"\+"),
    ("MINUS",    r"-"),
    ("LPAREN",   r"\("),
    ("RPAREN",   r"\)"),
    ("COMMA",    r","),
    ("SKIP",     r"[ \t]+"),
    ]
TOKEN_REGEX = "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC)

class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value
    def __repr__(self):
        return f"Token({self.type},{self.value})"

def tokenize(text):
    pos = 0
    while pos < len(text):
        mo = re.match(TOKEN_REGEX, text[pos:])
        if not mo:
            raise SyntaxError(f"Illegal character '{text[pos]}' at position {pos}")

        kind = mo.lastgroup
        value = mo.group()
        pos += len(value)

        if kind == "SKIP":
            continue

        if kind == "PREFIXED":
            prefix = value[1].lower()
            digits = value[2:]
            yield Token("NUMBER", convert_number(digits, prefix))

        elif kind == "NUMBER":
            yield Token("NUMBER", convert_number(value, 'd'))

        else:
            yield Token(kind, value)

    yield Token("EOF", None)

# --------------------------------------------
# Parser (precedence climbing with RPN output)
# --------------------------------------------
class ParserRPN:
    def __init__(self, text):
        self.tokens = list(tokenize(text))
        self.pos = 0
        self.current = self.tokens[self.pos]
        self.output = []

    def advance(self):
        self.pos += 1
        self.current = self.tokens[self.pos]

    def eat(self, type_):
        if self.current.type == type_:
            self.advance()
        else:
            raise SyntaxError(f"Expected {type_}, got {self.current.type}")

    def parse(self):
        self.expression()
        if self.current.type != "EOF":
            raise SyntaxError("Unexpected token after expression")
        return self.output

    def expression(self, min_prec=0):
        # Unary minus
        if self.current.type == "MINUS":
            self.advance()
            self.expression(100)
            self.output.append("NEG")
        else:
            self.primary()

        prec_table = {
            "POW": (4, True),
            "MUL": (3, False),
            "DIV": (3, False),
            "IDIV": (3, False),
            "PLUS": (2, False),
            "MINUS": (2, False),
        }

        while True:
            tok_type = self.current.type
            if tok_type not in prec_table:
                break
            prec, right_assoc = prec_table[tok_type]
            if prec < min_prec:
                break
            self.advance()
            next_min = prec if right_assoc else prec + 1
            self.expression(next_min)
            self.output.append({
                "PLUS": "+",
                "MINUS": "-",
                "MUL": "*",
                "DIV": "/",
                "IDIV": "//",
                "POW": "**",
            }[tok_type])

    def primary(self):
        tok = self.current
        if tok.type == "NUMBER":
            self.output.append(tok.value)
            self.advance()
        elif tok.type == "IDENT":
            name = tok.value
            self.advance()
            if self.current.type == "LPAREN":
                self.advance()
                args = self.argument_list()
                self.eat("RPAREN")
                for arg in args:
                    self.output.extend(arg)
                self.output.append((name, len(args)))
            else:
                self.output.append(name)
        elif tok.type == "LPAREN":
            self.advance()
            self.expression()
            self.eat("RPAREN")
        else:
            raise SyntaxError(f"Unexpected token {tok.type}")

    def argument_list(self):
        args = []
        if self.current.type == "RPAREN":
            return args
        args.append(self.expression_as_list())
        while self.current.type == "COMMA":
            self.advance()
            args.append(self.expression_as_list())
        return args

    def expression_as_list(self):
        old_output = self.output
        self.output = []
        self.expression()
        result = self.output
        self.output = old_output
        return result

# -----------
# Parsing API
# -----------
def to_rpn(expr):
    parser = ParserRPN(expr)
    return parser.parse()

def is_number(expr):
    try:
        rpn = to_rpn(expr)
        if len(rpn) == 1:
            if isinstance(rpn[0], int) or isinstance(rpn[0], float):
                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        pass ### print(type(e).__name__, str(e))
        return False       

def is_integer(expr):
    try:
        rpn = to_rpn(expr)
        if len(rpn) == 1:
            if isinstance(rpn[0], int):
                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        pass ### print(type(e).__name__, str(e))
        return False       

def is_expression(expr):
    try:
        rpn = to_rpn(expr)
        return True
    except Exception as e:
        pass ### print(type(e).__name__, str(e))
        return False

# ---------
# Evaluator
# ---------
def evaluate_rpn(tokens, variables=None):
    if variables is None:
        variables = {}
    stack = []
    funcs = {
        "shl": lambda x, n: x << n,
        "shr": lambda x, n: x >> n,
        "and": lambda x, y: x & y,
        "or":  lambda x, y: x | y,
        "xor": lambda x, y: x ^ y,
        "not": lambda x: ~x,
        "max": lambda *args: max(args),
    }
    for t in tokens:
        if isinstance(t, (int, float)):
            stack.append(t)
        elif t in variables:
            stack.append(variables[t])
        elif isinstance(t, tuple):
            name, argcount = t
            args = [stack.pop() for _ in range(argcount)][::-1]
            if name not in funcs:
                raise ValueError(f"Unknown function {name}")
            stack.append(funcs[name](*args))
        elif t in ('+', '-', '*', '/', '//', '**', 'NEG'):
            if t == '+': b=stack.pop(); a=stack.pop(); stack.append(a+b)
            elif t == '-': b=stack.pop(); a=stack.pop(); stack.append(a-b)
            elif t == '*': b=stack.pop(); a=stack.pop(); stack.append(a*b)
            elif t == '/': b=stack.pop(); a=stack.pop(); stack.append(a/b)
            elif t == '//': b=stack.pop(); a=stack.pop(); stack.append(a//b)
            elif t == '**': b=stack.pop(); a=stack.pop(); stack.append(a**b)
            elif t == 'NEG': a=stack.pop(); stack.append(-a)
        else:
            raise ValueError(f"Unknown RPN token '{t}'")
    if len(stack) != 1:
        raise ValueError("Invalid RPN expression")
    return stack[0]
