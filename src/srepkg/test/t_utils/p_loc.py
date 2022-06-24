# REFERENCE
# https://stackoverflow.com/questions/9186395/python-is-there-a-way-to-get-a-local-function-variable-from-within-a-decorator/9187022#9187022
# https://github.com/pberkes/persistent_locals
import sys


class PersistentLocals(object):
    def __init__(self, func):
        self._locals = {}
        self.func = func

    def __call__(self, *args, **kwargs):
        def tracer(frame, event, arg):
            if event == "return":
                self._locals = frame.f_locals.copy()

        # tracer is activated on next call, return or exception
        sys.setprofile(tracer)
        try:
            # trace the function call
            res = self.func(*args, **kwargs)
        finally:
            # disable tracer and replace with old one
            sys.setprofile(None)
        return res

    def clear_locals(self):
        self._locals = {}

    @property
    def locals(self):
        return self._locals


# Example Usage
# @PersistentLocals
# def func():
#     local1 = 1
#     local1 += 1
#     local2 = 2
#     return local2 + local1
#
# a = func()
# print(a)
# print(func.locals)
#
# OUTPUT:
# 4
# {'local1': 2, 'local2': 2}
