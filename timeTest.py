import time


def multiply_2(n):
    a = time.time()
    tmp = 1
    for i in range(n):
        tmp = tmp * 2
        tmp = tmp / 2
    b = time.time()
    print("multiply cost %.3f seconds" % (b - a))


def bit_2(n):
    a = time.time()
    tmp = 1
    for i in range(n):
        tmp = tmp << 1
        tmp = tmp >> 1
    b = time.time()
    print("bit move cost %.3f seconds" % (b - a))


n = 10 ** 8 # 来回乘除和位运算运行 1亿次，怎么乘除还快点???
multiply_2(n)
bit_2(n)