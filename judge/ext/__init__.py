# encoding: utf-8
import os

def _make_registry():
    _registry = {}

    def _reg(f):
        _registry[f.name] = f
        return f

    return _registry, _reg

registry, register = _make_registry()

__all__ = ['register', 'registry']

for module in os.listdir(os.path.dirname(__file__)):
    if module != '__init__.py' and module.endswith('.py'):
        module_name = module[:-3]
        mod = __import__('%s.%s' % (__name__, module_name),
                         globals(),
                         locals())
        __all__.append(module_name)
