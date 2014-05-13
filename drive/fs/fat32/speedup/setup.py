# encoding: utf-8
from Cython.Build import cythonize
from setuptools import setup

setup(ext_modules=cythonize('_op.pyx'))
