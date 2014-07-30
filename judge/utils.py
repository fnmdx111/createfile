# encoding: utf-8
from datetime import timedelta
from functools import reduce

from .dummy import _
from .abbr import SI_ALL, FN_ALL


_g = lambda n: getattr(_, n)


def _flatten_args(ns):
    ret = []
    for n in ns:
        if isinstance(n, list):
            ret.extend(map(_g, n))
        else:
            ret.append(_g(n))

    return ret


def max_(*ns):
    return reduce(lambda acc, w: acc.__max__(w), _flatten_args(ns))


def min_(*ns):
    return reduce(lambda acc, w: acc.__min__(w), _flatten_args(ns))


def approx_eq(*ns, error=timedelta(seconds=2)):
    ts = _flatten_args(ns)

    t0, t1 = ts[0], ts[1]
    expr = abs(t1 - t0) <= error

    for t in ts[2:]:
        expr &= abs(t - t0) <= error

    return expr
axe = approx_eq


def ntfs_mace_congruent(_=_):
    return approx_eq(SI_ALL, FN_ALL)
nmc = ntfs_mace_congruent


def ctg_eq(name):
    """Category equivalency."""
    return approx_eq('si_%s_time' % name,
                     'fn_%s_time' % name)
ce = ctg_eq


def attr_eq(name):
    """Attribute equivalency."""
    return approx_eq(*map(lambda n: '%s_%s_time' % (name, n),
                          ['create', 'modify', 'access', 'mft']))
ate = attr_eq
