# encoding: utf-8
from collections import OrderedDict


class Cache:
    def __init__(self, size):
        self._c = OrderedDict()
        self._size = size

    def insert(self, k, v):
        self._c[k] = v

        if len(self._c) > self._size:
            self._c.popitem(last=False)

    def exists(self, k):
        return k in self._c

    def touch(self, k):
        v = self._c[k]
        del self._c[k]

        self._c[k] = v

    def get(self, k):
        return self._c[k]
