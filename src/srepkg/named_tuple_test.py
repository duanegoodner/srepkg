from typing import NamedTuple


class TestThing(NamedTuple):
    param_1: str
    param_2: str
    param_3: int


class AnotherThing(TestThing):
    param_4: int


print(dir(TestThing))

print(TestThing._fields)
print(type(TestThing._fields[2]))

print(AnotherThing.index)
