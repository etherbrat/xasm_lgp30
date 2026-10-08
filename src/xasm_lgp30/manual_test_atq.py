from xasm_lgp30.lgp30_atq import python2atq, atq2python

while True:
    value = float(input('value --> '))
    q_value = int(input('q-value -->'))
    try:
        atq_value = python2atq(value, q_value)
    except Exception as e:
        atq_value = 0
        print(type(e).__name__, str(e))
    print(f"{atq_value:08x}")
    print(atq2python(atq_value, q_value))
