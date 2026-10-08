XASM_LGP30_VERSION = '1.0'
DEBUG = True # for debugging purposes only
LIST_HEX = True # set false to show only sexadecimal
LISTING_TAB_INTERVAL = 4 # for source files with tabs

import re
SYMBOL_PATTERN = re.compile(r"_?[A-Za-z][A-Za-z0-9_]*")

# address-related
MIN_ADDR = 0
MAX_ADDR = 4095
DEFAULT_LOCATION_PTR = 0

# track-value-related
MIN_TRACK = 0
MAX_TRACK = 63
MIN_SECTOR = 0
MAX_SECTOR = 63

# these delineate LGP-30 integer values
# but are expressed as native Python values
MIN_INTEGER = -(2**31)
MAX_INTEGER = (2**31)-1
# this delineates a 31-bit quantity
FULL_WORD = 0xffffffff # chop to 32 bits
WORD_MASK = 0xfffffffe # chop to 32 bits and zero the lsb
SIGN_MASK = 0x80000000 # isolate the sign bit
# q value constraints
MIN_Q_VALUE = 0
MAX_Q_VALUE = 30
# shift constraints
MIN_SHIFT_VALUE = 1
MAX_SHIFT_VALUE = 30
# switch mask constraints
SW32 = 0x20
SW16 = 0x10
SW8 = 0x8
SW4 = 0x4

# tuple indices for argument constraint validation
TYPE_VALIDATOR = 0

# symbol prefixes
symbol_prefixes = {
    '_':0
    }
# binary character set
bin_charset = {
    '0':0,
    '1':1
    }

# octal character set
oct_charset = {
    '0':0,
    '1':1,
    '2':2,
    '3':3,
    '4':4,
    '5':5,
    '6':6,
    '7':7
    }

# decimal character set
dec_charset = {
    '0':0,
    '1':1,
    '2':2,
    '3':3,
    '4':4,
    '5':5,
    '6':6,
    '7':7,
    '8':8,
    '9':9
    }

# LGP-30 sexadeciaml character set
sex_charset = {
    '0':0,
    '1':1,
    '2':2,
    '3':3,
    '4':4,
    '5':5,
    '6':6,
    '7':7,
    '8':8,
    '9':9,
    'f':10,
    'g':11,
    'j':12,
    'k':13,
    'q':14,
    'w':15
    }

# hexadecimal character set
hex_charset = {
    '0':0,
    '1':1,
    '2':2,
    '3':3,
    '4':4,
    '5':5,
    '6':6,
    '7':7,
    '8':8,
    '9':9,
    'a':10,
    'b':11,
    'c':12,
    'd':13,
    'e':14,
    'f':15
    }
    
# character code range
MIN_CHAR_CODE = 0
MAX_CHAR_CODE = 63
# tuple indices for output character set mapping
LGP30_ADDRESS_CODE = 0
TRACK_DECIMAL_CODE = 1
FRIDEN_DESCRIPTION = 2
FRIDEN_NOTE = 3
# output character set mapping to Friden codes
output_charset = {
    '#~':(300,3,'space',''),
    '"':(1400,14,'',''),
    '$':(2600,26,'dollar',''),
    '%':(2200,22,'',''),
    '(':(3800,38,'',''),
    ')':(200,2,'',''),
    '*':(1000,10,'',''),
    ',':(2700,27,'',''),
    '.':(2300,23,'',''),
    '/':(1900,19,'',''),
    '#1':(1500,15,'colon',''),
    '#2':(1500,15,'semicolon',''),
    '?':(1900,19,'',''),
    '[':(2700,27,'',''),
    '#b':(2000,20,'backspace','not used in input'),
    '#c':(1200,12,'colour shift','not used in input'),
    '#d':(1800,18,'Δ (delta)',''),
    '#l':(400,4,'lower case','not used in input'),
    '#n':(1600,16,'carriage return','not used in input'),
    '#p':(3000,30,'∏ (pi)',''),
    '#r':(0,0,'start read','not used in input'),
    '#s':(3400,34,'Σ (sigma)',''),
    '#t':(2400,24,'tab',''),
    '#u':(800,8,'upper case','not used in input'),
    '#x':(6300,63,'delete','not used in input'),
    "'":(3200,32,'conditional stop','not used in input'),
    ']':(2300,23,'',''),
    '_':(700,7,'',''),
    '-':(700,7,'',''),
    '+':(1100,11,'',''),
    '=':(1100,11,'',''),
    '0':(200,2,'',''),
    '1':(600,6,'',''),
    '2':(1000,10,'',''),
    '3':(1400,14,'',''),
    '4':(1800,18,'',''),
    '5':(2200,22,'',''),
    '6':(2600,26,'',''),
    '7':(3000,30,'',''),
    '8':(3400,34,'',''),
    '9':(3800,38,'',''),
    'A':(5700,57,'',''),
    'a':(5700,57,'',''),
    'B':(500,5,'',''),
    'b':(500,5,'',''),
    'C':(5300,53,'',''),
    'c':(5300,53,'',''),
    'D':(2100,21,'',''),
    'd':(2100,21,'',''),
    'E':(3700,37,'',''),
    'e':(3700,37,'',''),
    'F':(4200,42,'',''),
    'f':(4200,42,'',''),
    'G':(4600,46,'',''),
    'g':(4600,46,'',''),
    'H':(4900,49,'',''),
    'h':(4900,49,'',''),
    'I':(1700,17,'',''),
    'i':(1700,17,'',''),
    'J':(5000,50,'',''),
    'j':(5000,50,'',''),
    'K':(5400,54,'',''),
    'k':(5400,54,'',''),
    'L':(600,6,'',''),
    'l':(600,6,'','Same as 1, like a typewriter'),
    'M':(2900,29,'',''),
    'm':(2900,29,'',''),
    'N':(2500,25,'',''),
    'n':(2500,25,'',''),
    'O':(3500,35,'',''),
    'o':(3500,35,'',''),
    'P':(3300,33,'',''),
    'p':(3300,33,'',''),
    'Q':(5800,58,'',''),
    'q':(5800,58,'',''),
    'R':(1300,13,'',''),
    'r':(1300,13,'',''),
    'S':(6100,61,'',''),
    's':(6100,61,'',''),
    'T':(4500,45,'',''),
    't':(4500,45,'',''),
    'U':(4100,41,'',''),
    'u':(4100,41,'',''),
    'V':(3100,31,'',''),
    'v':(3100,31,'',''),
    'W':(6200,62,'',''),
    'w':(6200,62,'',''),
    'X':(3900,39,'',''),
    'x':(3900,39,'',''),
    'Y':(900,9,'',''),
    'y':(900,9,'',''),
    'Z':(100,1,'',''),
    'z':(100,1,'','')    
    }

# tuple indices for opcode dictionary
OPCODE_CHAR = 0
OPCODE_NUM_ARGS = 1
OPCODE_ARG_CONSTRAINTS = 2
OPCODE_PROCESSOR = 3
OPCODE_VAL = 4

# Instructions with an address operand
# In the LGP-30 bit 0 is the high bit
# Opcode -> bits 12-15, memory address -> bits 18-29
# |00000000001111111111222222222233|
# |01234567890123456789012345678901| LGP-30 bit numbers
# |s           oooo  aaaaaaaaaaaa x| s = sign, x = spacer
# |33222222222211111111110000000000| int bit numbers
# |10987654321098765432109876543210|
# In a 32-bit int these are bits 19-16 and 13-2
# Hence:
# left shift counts for binary assembly
ASM_OPCODE_SHIFT = 16
ASM_OPCODE_MASK = 0x000f0000
ASM_ADDRESS_SHIFT = 2
ASM_ADDRESS_MASK = 0x00003ffc

# Instructions with a track operand
# Opcode -> bits 12-15, track -> bits 18-23
# |00000000001111111111222222222233|
# |01234567890123456789012345678901|LGP-30 bit numbers
# |s           oooo  tttttt        | s = sign, x = spacer
# |33222222222211111111110000000000| int bit numbers
# |10987654321098765432109876543210|
# In a 32-bit int these are bits 19-16 and 13-8
# Hence:
# left shift count for binary assembly
ASM_TRACK_SHIFT = 8
ASM_TRACK_MASK = 0x00003f00

# constants for Intel hex output
HEX_PER_WORD = 8
BITS_PER_HEX = 4
HEX_MASK = 0xf
BYTES_PER_HEX_RECORD = 16
