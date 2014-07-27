# encoding: utf-8

from .wrappers import AttributeWrapper, AttributeWrapperEx,\
                      all_, any_, every, some
from .misc import id_

from datetime import datetime as dt, datetime, timedelta as td, timedelta,\
    date, time

__all__ = ['If', '_', '_1', '_2', 'DummyEntry',
           'all_', 'any_', 'every', 'some', 'ext',
           'dt', 'datetime', 'td', 'timedelta', 'time', 'date']


class DummyEntry:
    """
    A dummy entry class for rule definition mechanism.
    """
    def __init__(self, name='_'):
        self.name = name

    def __getattr__(self, item):
        return AttributeWrapper(item, self)

# universal dummy entry
_ = DummyEntry()


class DummyEntryEx:
    def __init__(self, name):
        self.name = name

    def __getattr__(self, item):
        return AttributeWrapperEx(item, self)

_1, _2 = DummyEntryEx('_1'), DummyEntryEx('_2')


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
