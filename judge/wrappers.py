# encoding: utf-8
import operator
from .misc import id_


class AbstractWrapper:
    def __init__(self):
        for kw in ['lt', 'le', 'eq', 'ne', 'gt', 'ge']:
            self.install_binary('__%s__' % kw, getattr(operator, kw))
        self.install_binary('__and__', operator.and_)
        self.install_binary('__or__', operator.or_)

    def install_binary(self, name, op):
        dummy = self.gen_dummy(op)
        dummy.__name__ = name
        setattr(type(self), name, dummy)

    def gen_dummy(self, op):
        raise NotImplementedError


class PredicateWrapper(AbstractWrapper):
    def __init__(self, predicate=id_):
        super(PredicateWrapper, self).__init__()

        self.predicate = predicate

    def gen_dummy(self, op):
        def dummy(self_, other):
            if type(other) != type(self_):
                other_ = lambda _: other
            else:
                other_ = other.predicate

            return PredicateWrapper(lambda x: op(self_.predicate(x),
                                                 other_(x)))

        return dummy

    def __neg__(self):
        return PredicateWrapper(lambda x: not self.predicate(x))

    def __call__(self, *args, **kwargs):
        return self.predicate(*args, **kwargs)


class AttributeWrapper(AbstractWrapper):
    def __init__(self, name, parent):
        super(AttributeWrapper, self).__init__()
        self.name = name
        self.parent = parent

    def gen_dummy(self, op):
        def dummy(self_, other):
            if type(other) == type(self_):
                other_ = lambda x: getattr(x, other.name)
            elif type(other) == type(id_):
                other_ = other
            else:
                other_ = lambda _: other
            return PredicateWrapper(lambda x: op(getattr(x, self_.name),
                                                 other_(x)))

        return dummy

    def __neg__(self):
        return PredicateWrapper(lambda x: not getattr(x, self.name))
