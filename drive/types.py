# encoding: utf-8
"""
    drive.types
    ~~~~~~~~~~~

    This module implements the type registration mechanism.
"""

def _make_registry():
    _registry = {}

    def _reg(_type):
        def _wrapper(f):
            _registry[_type] = f
            return f
        return _wrapper

    return _registry, _reg

registry, register = _make_registry()
