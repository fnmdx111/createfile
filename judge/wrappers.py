# encoding: utf-8
from datetime import datetime
import operator

from .misc import id_, wrapper_func, predicate_od_func, \
    attribute_od_func, getattr_, approximate_seconds


class AbstractWrapper:
    def __init__(self, expr):
        self.expr = expr

        def ne(x, y):
            if isinstance(x, datetime) and isinstance(y, datetime):
                return abs(x - y) > approximate_seconds
            else:
                return x == y

        def eq(x, y):
            if isinstance(x, datetime) and isinstance(y, datetime):
                return abs(x - y) < approximate_seconds
            else:
                return x == y

        def lt(x, y):
            if isinstance(x, datetime) and isinstance(y, datetime):
                return x < y and (y - x) > approximate_seconds
            else:
                return x < y

        def gt(x, y):
            if isinstance(x, datetime) and isinstance(y, datetime):
                return x > y and (x - y) > approximate_seconds
            else:
                return x > y

        def le(x, y):
            if isinstance(x, datetime) and isinstance(y, datetime):
                return eq(x, y) or lt(x, y)
            else:
                return x <= y

        def ge(x, y):
            if isinstance(x, datetime) and isinstance(y, datetime):
                return eq(x, y) or gt(x, y)
            else:
                return x >= y

        for kw in ['add', 'sub']:
            self.install_binary('__%s__' % kw, getattr_(operator, kw))
        self.install_binary('__and__', operator.and_)
        self.install_binary('__or__', operator.or_)
        self.install_binary('__max__', max)
        self.install_binary('__min__', min)
        self.install_binary('__eq__', eq)
        self.install_binary('__ne__', ne)
        self.install_binary('__lt__', lt)
        self.install_binary('__gt__', gt)
        self.install_binary('__le__', le)
        self.install_binary('__ge__', ge)

    def install_binary(self, name, op):
        dummy = self.gen_dummy(op)
        dummy.__name__ = name
        setattr(type(self), name, dummy)

    def gen_dummy(self, op):
        raise NotImplementedError


def install_misc(cls, wrapper_cls, wrapper_f, operand_f):
    def gen_unary(op):
        def dummy(self_):
            # lambda x: wrapper_f(op, operand_f(self_, x))
            # lambda xs: wrapper_f(op, operand_f(self_, x))
            # wrapper_f = lambda op, od: op(od)
            # wrapper_f = lambda op, od: map(op, od)

            return wrapper_cls(lambda _: wrapper_f(op,
                                                   operand_f(self_, _)),
                               '%s(%s)' % (op.__name__,
                                           self_.expr))
        return dummy

    for kw in ['neg', 'abs']:
        _ = gen_unary(getattr_(operator, kw))
        _.__name__ = '__%s__' % kw
        setattr(cls, _.__name__, _)

    def getitem(self_, item):
        return wrapper_cls(
            lambda _: wrapper_f(lambda x: operator.getitem(x, item),
                                operand_f(self_, _)),
            '%s[%s]' % (self_.expr, item)
        )
    getitem.__name__ = '__getitem__'
    setattr(cls, getitem.__name__, getitem)


class PredicateWrapper(AbstractWrapper):
    def __init__(self, predicate=id_, expr=''):
        super(PredicateWrapper, self).__init__(expr)

        self.predicate = predicate

    def gen_dummy(self, op):
        def dummy(self_, other):
            def patch(op_, o1, o2):
                # TODO remove this patch asap
                if op_.__name__ == 'and_':
                    return o1 and o2
                elif op_.__name__ == 'or_':
                    return o1 or o2
                else:
                    return op_(o1, o2)

            if isinstance(other, AttributeWrapper):
                other_ = lambda x: attribute_od_func(other, other.obj(x))
                other_expr = other.expr
            elif type(other) != type(self_):
                other_ = lambda _: other
                other_expr = other
            else:
                other_ = other.predicate
                other_expr = other.expr

            expr = '%s(%s, %s)' % (op.__name__,
                                   self_.expr,
                                   other_expr)

            return PredicateWrapper(lambda x: patch(op,
                                                    self_.predicate(x),
                                                    other_(x)),
                                    expr)

        return dummy

    def __call__(self, *args, **kwargs):
        return self.predicate(*args, **kwargs)

install_misc(PredicateWrapper,
             PredicateWrapper,
             wrapper_func,
             predicate_od_func)


class AttributeWrapper(AbstractWrapper):
    def __init__(self, name, parent, obj=id_, expr='', non_attr=False):
        super(AttributeWrapper, self).__init__(expr)

        self.name = name
        self.parent = parent
        self.obj = obj

        self.expr = expr or '%s.%s' % (self.parent.name, self.name)

        self.non_attr = non_attr

    def gen_dummy(self, op):
        def dummy(self_, other):
            if self.non_attr:
                n = lambda x: self_.obj(x)
            else:
                n = lambda x: getattr_(self_.obj(x), self_.name)

            if type(other) == type(self_):
                if other.non_attr:
                    other_ = lambda x: other.obj(x)
                else:
                    other_ = lambda x: getattr_(other.obj(x), other.name)
                other_expr = other.expr
            elif type(other) == type(id_):
                other_ = other
                other_expr = other
            elif isinstance(other, PredicateWrapper):
                other_ = other.predicate
                other_expr = other.expr
            elif isinstance(other, Probe):
                other_ = lambda x: print(n(x))
                other_expr = ''
            else:
                other_ = lambda _: other
                other_expr = other

            return PredicateWrapper(lambda x: op(n(x),
                                                 other_(x)),
                                    '%s(%s, %s)' % (op.__name__,
                                                    self_.expr,
                                                    other_expr))

        return dummy

    def __call__(self, *args, **kwargs):
        return AttributeWrapper('', self,
                                obj=lambda x: getattr_(self.obj(x),
                                                       self.name)(*args,
                                                                  **kwargs),
                                non_attr=True)

    def __getattr__(self, item):
        return AttributeWrapper(item, self, obj=lambda x: getattr_(self.obj(x),
                                                                  self.name))
install_misc(AttributeWrapper,
             PredicateWrapper,
             wrapper_func,
             attribute_od_func)


class Probe:
    pass
