# encoding: utf-8
from itertools import combinations

id_ = lambda _: _

wrapper_func = lambda op, od: op(od)

def getattr_(x, n):
    if n == '':
        return x
    else:
        return getattr(x, n)

predicate_od_func = lambda self, x: self.predicate(x)
attribute_od_func = lambda self, x: getattr_(x, self.name)
