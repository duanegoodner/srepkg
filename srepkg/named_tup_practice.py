from collections import namedtuple
from typing import NamedTuple


A = namedtuple('A', ['a', 'b'])

test_a = A(a=1, b='hello')

test_a2 = A(1, 2)

print(test_a2)






