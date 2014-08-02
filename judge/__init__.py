# encoding: utf-8

from datetime import datetime as dt, datetime, timedelta as td, timedelta,\
    date, time

from .dummy import _
from .utils import max_, min_, approx_eq, ntfs_mace_congruent, ctg_eq, attr_eq,\
    axe, nmc, ce, ate
from .abbr import _c_, _m_, _a_, _e_, _si_, _fn_, si_e, si_m, si_a, si_c,\
    fn_e, fn_m, fn_a, fn_c, f_c, f_a, f_m, C, M, A, E, SI, FN,\
    SI_E, SI_M, SI_A, SI_C, FN_E, FN_M, FN_A, FN_C, F_C, F_M, F_A,\
    SI_ALL, FN_ALL, F_ALL, M_ALL, C_ALL, E_ALL, A_ALL
from .misc import id_


__all__ = ['If', '_',
           'ext', 'max_', 'min_', 'approx_eq', 'axe',
           'ntfs_mace_congruent', 'nmc', 'ctg_eq', 'ce', 'attr_eq', 'ate',
           '_m_', '_a_', '_c_', '_e_', '_si_', '_fn_',
           'si_a', 'si_c', 'si_m', 'si_e', 'fn_a', 'fn_c', 'fn_m', 'fn_e',
           'f_a', 'f_c', 'f_m',
           'C', 'M', 'A', 'E', 'SI', 'FN',
           'SI_E', 'SI_M', 'SI_A', 'SI_C', 'FN_E', 'FN_M', 'FN_A', 'FN_C',
           'F_C', 'F_A', 'F_M',
           'SI_ALL', 'FN_ALL', 'F_ALL', 'M_ALL', 'C_ALL', 'E_ALL', 'A_ALL',
           'dt', 'datetime', 'td', 'timedelta', 'time', 'date']


class JudgedEntry:
    def __init__(self, entry, conclusions=None):
        self.entry = entry
        self.conclusions = conclusions or []

    def append_conclusion(self, conclusion):
        self.conclusions.append(conclusion)

    def merge(self, other):
        self.conclusions.extend(other.conclusions)


class Rule:
    def __init__(self, predicate):
        self.predicate = predicate

        self.result = []
        self.positives = []
        self.e = None

    def then(self, conclusion='', abnormal=False):
        self.conclusion = conclusion
        self.abnormal = abnormal

        return self

    def _pending_return_values(self, e):
        self.result = [JudgedEntry(o) for _, o in e.iterrows()]
        self.positives = []
        self.e = e

    def mark_as_positive(self, i):
        self.positives.append(i)
        self.result[i].append_conclusion(self.conclusion)

    def do_apply(self, entries):
        for i, (ts, obj) in enumerate(entries.iterrows()):
            if self.predicate(obj):
                self.mark_as_positive(i)

    def apply_to(self, entries):
        self._pending_return_values(entries)

        self.do_apply(entries)

        return self.result, self.positives, self.e

If = Rule
