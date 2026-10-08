from collections import deque
from validate_funcsV1  import is_symbol

context = {}
context['error_queue'] = deque()

while True:
    string = input('--> ').strip()
    print(is_symbol(context, string))
    