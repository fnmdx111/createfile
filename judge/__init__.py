# encoding: utf-8

from .wrappers import AttributeWrapper, AttributeWrapperEx,\
                      all_, any_, every, some
from .misc import id_

__all__ = ['If', '_', '_1', '_2', 'DummyEntry',
           'all_', 'any_', 'every', 'some']


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


class Rule:
    def __init__(self, predicate, name=''):
        self.predicate = predicate
        self.name = name

        self.conclusion = ''
        self.action = id_

    def then(self, conclusion='', action=id_):
        self.conclusion = conclusion
        self.action = action

        return self

    def apply_to(self, entries):
        conclusions, result = [], []
        for ts, obj in entries.iterrows():
            c, r = '', None
            if self.predicate(obj):
                c = self.conclusion
                r = self.action(obj)

            conclusions.append(c)
            result.append(r)

        return conclusions, result

    def apply(self, obj):
        if self.predicate(obj):
            return self.conclusion, self.action(obj)
        else:
            return '', None

If = Rule
