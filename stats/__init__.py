# encoding: utf-8
from itertools import islice
from .speedup.kendall import u_tau


def windowed(l, size=5, step=1):
    while len(l) >= size:
        yield islice(l, size)
        del l[:step]
