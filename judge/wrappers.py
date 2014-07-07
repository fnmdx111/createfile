# encoding: utf-8
from functools import partial
from itertools import repeat, product
import operator
from .misc import id_, wrapper_func, ex_wrapper_func, predicate_od_func, \
    attribute_od_func, combinations_ex


class AbstractWrapper:
    def __init__(self, expr):
        self.expr = expr

        for kw in ['lt', 'le', 'eq', 'ne', 'gt', 'ge', 'add', 'sub']:
            self.install_binary('__%s__' % kw, getattr(operator, kw))
        self.install_binary('__and__', operator.and_)
        self.install_binary('__or__', operator.or_)

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
        _ = gen_unary(getattr(operator, kw))
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

            if isinstance(other, PredicateWrapperEx):

                raise NotImplementedError
                # return PredicateWrapperEx(
                #     # avoid comparing between PW and PWE objects
                #     # all or any is not decidable
                #     lambda xs: patch(op,
                #                      all(map(self.predicate, xs)),
                #                      other.predicate(xs)),
                #     '%s(%s, %s)' % (op.__name__, self_.expr, other.expr)
                # )
            elif isinstance(other, AttributeWrapper):
                other_ = lambda x: attribute_od_func(other, x)
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

    def __all__(self):
        return PredicateWrapperEx(lambda xs: [all(map(self.predicate,
                                                      xs))],
                                  'all(%s)' % self.expr)

    def __any__(self):
        return PredicateWrapperEx(lambda xs: [any(map(self.predicate,
                                                      xs))],
                                  'any(%s)' % self.expr)

install_misc(PredicateWrapper,
             PredicateWrapper,
             wrapper_func,
             predicate_od_func)


class AttributeWrapper(AbstractWrapper):
    def __init__(self, name, parent, expr=''):
        super(AttributeWrapper, self).__init__(expr)

        self.name = name
        self.parent = parent

        self.expr = expr or '%s.%s' % (self.parent.name, self.name)

    def gen_dummy(self, op):
        def dummy(self_, other):
            if type(other) == type(self_):
                other_ = lambda x: getattr(x, other.name)
                other_expr = other.expr
            elif type(other) == type(id_):
                other_ = other
                other_expr = other
            elif isinstance(other, PredicateWrapper):
                other_ = other.predicate
                other_expr = other.expr
            else:
                other_ = lambda _: other
                other_expr = other

            return PredicateWrapper(lambda x: op(getattr(x, self_.name),
                                                 other_(x)),
                                    '%s(%s, %s)' % (op.__name__,
                                                    self_.expr,
                                                    other_expr))

        return dummy

install_misc(AttributeWrapper,
             PredicateWrapper,
             wrapper_func,
             attribute_od_func)


class PredicateWrapperEx(AbstractWrapper):
    def __init__(self, predicate=id_, expr=''):
        super(PredicateWrapperEx, self).__init__(expr)

        self.predicate = predicate

    def gen_dummy(self, op):
        def dummy(self_, other):
            if type(other) == type(self_):
                return PredicateWrapperEx(
                    lambda xs: map(lambda _: op(_[0], _[1]),
                                   product(self_.predicate(xs),
                                           other.predicate(xs))),
                    '%s(%s, %s)' % (op.__name__,
                                    self_.expr,
                                    other.expr)
                )
            else:
                return PredicateWrapperEx(
                    lambda xs: map(lambda _: op(*_),
                                   zip(self_.predicate(xs),
                                       repeat(other))),
                    '%s(%s, %s)' % (op.__name__,
                                    self_.expr,
                                    other)
                )

        return dummy

    def __call__(self, *args, **kwargs):
        return self.predicate(*args, **kwargs)

    def __all__(self):
        return PredicateWrapperEx(lambda xs: [all(self.predicate(xs))],
                                  'all(%s)' % self.expr)

    def __any__(self):
        return PredicateWrapperEx(lambda xs: [any(self.predicate(xs))],
                                  'any(%s)' % self.expr)

install_misc(PredicateWrapperEx,
             PredicateWrapperEx,
             ex_wrapper_func,
             predicate_od_func)


class AttributeWrapperEx(AbstractWrapper):
    def __init__(self, name, parent, expr=''):
        super(AttributeWrapperEx, self).__init__(expr)

        self.name = name
        self.parent = parent

        self.expr = expr or '%s.%s' % (self.parent.name, self.name)

    def gen_dummy(self, op):
        def dummy(self_, other):
            other_expr = other
            if type(other) == type(self_):
                other_expr = other.expr
                coll = lambda xs: combinations_ex(
                    xs,
                    partial(map,
                            lambda x: getattr(x, self_.name)),
                    partial(map,
                            lambda x: getattr(x, other.name))
                )
            elif isinstance(other, PredicateWrapperEx):
                other_expr = other.expr
                coll = lambda xs: zip(map(lambda x: getattr(x, self_.name),
                                          xs),
                                      other.predicate(xs))
            else:
                coll = lambda xs: zip(map(lambda x: getattr(x, self_.name),
                                          xs),
                                      repeat(other))

            return PredicateWrapperEx(
                lambda xs: map(lambda _: op(*_),
                               coll(xs)),
                '%s(%s, %s)' % (op.__name__, self_.expr, other_expr)
            )

        return dummy

install_misc(AttributeWrapperEx,
             PredicateWrapperEx,
             ex_wrapper_func,
             attribute_od_func)

all_ = lambda w: w.__all__()
every = all_

any_ = lambda w: w.__any__()
some = any_
