# encoding: utf-8
"""
    stats.misc
    ~~~~~~~~~~

    This module implements the miscellaneous functions for :package:`stats`.
"""
from itertools import islice
from math import floor


def windowed(l, size=5, step=1):
    """Break the sequence in windows, e.g.::

        >>> list(windowed([1, 2, 3, 4, 5],
        ...               size=3, step=1))
        [[1, 2, 3], [2, 3, 4], [3, 4, 5]]

    Note that step larger than size may result in unwanted error.

    :param l: the sequence to be windowed, which must support
             slicing protocol.
    :param size: the size of the window.
    :param step: the step between the window.
    """

    while len(l) >= size:
        yield islice(l, size)
        del l[:step]
    else:
        if len(l) > 1:
            yield l


def segmented(l, width=5, strict=True):
    """Segment the sequence into segments, e.g.::

        >>> list(segmented([1, 2, 3, 4, 5, 6, 7], width=5, strict=False))
        [((0, 1), (0, 1, 2), [1, 2, 3]),
         ((1, 2), (0, 1, 2, 3), [1, 2, 3, 4]),
         ((2, 3), (0, 1, 2, 3, 4), [1, 2, 3, 4, 5]),
         ((3, 4), (1, 2, 3, 4, 5), [2, 3, 4, 5, 6]),
         ((4, 5), (2, 3, 4, 5, 6), [3, 4, 5, 6, 7]),
         ((5, 6), (3, 4, 5, 6), [4, 5, 6, 7]),
         ((6, 7), (4, 5, 6), [5, 6, 7])]
        >>> list(segmented([1, 2, 3, 4, 5, 6, 7], width=5))
        [((2, 3), (0, 1, 2, 3, 4), [1, 2, 3, 4, 5]),
         ((3, 4), (1, 2, 3, 4, 5), [2, 3, 4, 5, 6]),
         ((4, 5), (2, 3, 4, 5, 6), [3, 4, 5, 6, 7])]

    :param l: the sequence to be segmented.
    :param width: optional, the width of the segments.
    :param strict: optional, if True, only segments with the exact width will
                   be yielded.
    """

    # convert even width to odd width by subtracting 1
    width = width if width % 2 else width - 1

    sw = floor(width / 2)
    ll = len(l)
    for x, y in enumerate(l):
        left = max(0, x - sw)
        right = min(x + sw + 1, ll)

        if not strict or right - left == width:
            # this equals `not (strict and right - left != width)`
            yield (x, y), (range(left, right), l[left:right])
