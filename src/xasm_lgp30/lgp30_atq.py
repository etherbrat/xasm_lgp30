from xasm_lgp30.assembler_constants import *

import math # for math.modf()

def atq2python(frac, q):
    # sign exend if necessary
    if frac & SIGN_MASK:
        return (0 - ((frac ^ FULL_WORD) + 1)) * 2**(q-31)
    else:
        return frac * 2**(q-31)
        
def python2atq(value, q):
    (f, i) = math.modf(value / (2**q))
    if i != 0:
        raise ValueError(f"{value} is non-fractional at q = {q}")
    else: 
        return int(f * 2**31) & WORD_MASK
