# encoding: utf-8
from itertools import combinations

id_ = lambda _: _

wrapper_func = lambda op, od: op(od)
ex_wrapper_func = lambda op, od: map(op, od)

predicate_od_func = lambda self, x: self.predicate(x)
attribute_od_func = lambda self, x: getattr(x, self.name)

def combinations_ex(xs, p1, p2):
    xs = list(xs)

    cs = combinations(range(len(xs)), 2)
    p1s, p2s = list(p1(xs)), list(p2(xs))

    for i, j in cs:
        yield p1s[i], p2s[j]
