# encoding: utf-8
from .wrappers import AttributeWrapper


class DummyEntry:
    """
    A dummy entry class for rule definition mechanism.
    """

    __abbr__ = {'c': 'create_time',
                'm': 'modify_time',
                'a': 'access_date'}

    for abbr, full in zip(['c', 'm', 'a', 'e'],
                          ['create', 'modify', 'access', 'mft']):
        for attr in ['si', 'fn']:
            __abbr__['%s_%s' % (attr, abbr)] = '%s_%s_time' % (attr, full)

    _upper = {}
    for k, v in __abbr__.items():
        _upper[k.upper()] = v

    __abbr__.update(_upper)

    def __init__(self, name='_'):
        self.name = name

    def __getattr__(self, item):
        if item in self.__abbr__:
            item = self.__abbr__[item]

        return AttributeWrapper(item, self)

# universal dummy entry
_ = DummyEntry()
