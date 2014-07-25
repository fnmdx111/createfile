# encoding: utf-8

def _make_registry():
    _registry = {}

    def _reg(f):
        _registry[f.NAME] = f
        return f

    return _registry, _reg

registry, register = _make_registry()
