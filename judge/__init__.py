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
    def __init__(self, predicate, name=''):
        self.predicate = predicate
        self.name = name

        self.conclusion = ''
        self.action = id_
        self.abnormal = False

    def then(self, conclusion='', action=id_, abnormal=False):
        self.conclusion = conclusion
        self.action = action
        self.abnormal = abnormal

        return self

    def apply_to(self, entries):
        result, positives = [], []
        for i, (ts, obj) in enumerate(entries.iterrows()):
            if self.predicate(obj):
                positives.append(i)
                result.append(JudgedEntry(obj, [self.conclusion]))
            else:
                result.append(JudgedEntry(obj))

        return result, positives

    def apply(self, obj):
        if self.predicate(obj):
            return self.conclusion, self.action(obj)
        else:
            return '', None

If = Rule
