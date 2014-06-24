# encoding: utf-8
from itertools import islice


def windowed(l, size=5, step=1):
    """`l' must support slicing protocol"""
    while len(l) >= size:
        yield islice(l, size)
        del l[:step]
