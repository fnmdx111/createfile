# encoding: utf-8
"""
    stats.misc
    ~~~~~~~~~~

    This module implements the miscellaneous functions for :package:`stats`.
"""
from itertools import islice


def windowed(l, size=5, step=1):
    """Break the sequence in windows, e.g.::

        >>> print(list(windowed([1, 2, 3, 4, 5],
        ...                     size=3, step=1)))
        [[1, 2, 3], [2, 3, 4], [3, 4, 5]]

    :param l: the sequence to be windowed, which must support
             slicing protocol.
    :param size: the size of the window.
    :param step: the step between the window.
    """

    while len(l) >= size:
        yield islice(l, size)
        del l[:step]
