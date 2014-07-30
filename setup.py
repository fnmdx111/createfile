# encoding: utf-8
from Cython.Build import cythonize
from setuptools import setup, Extension, find_packages
import numpy as np


extensions = [Extension('stats.speedup.alg',
                        ['stats/speedup/alg.pyx'],
                        include_dirs=[np.get_include()]),
              Extension('drive.fs.fat32.speedup._op',
                        ['drive/fs/fat32/speedup/_op.pyx'])]

setup(
    name='createfile',
    version='0.3.0',
    url='https://github.com/mad4alcohol/createfile',
    license='GNU LGPLv3',
    author='mad4a',
    author_email='chsc4698@gmail.com',
    description='',

    py_modules=['misc', 'bootstrap'],
    include_package_data=True,
    packages=find_packages(exclude=['test']),
    ext_modules=cythonize(extensions),

    entry_points={'gui_scripts': ['createfile = bootstrap:main']},

    install_requires=['Cython',
              'scipy',
              'matplotlib',
              'pyparsing',
              'PySide',
              'Jinja2',
              'construct',
              'PyWin32',
              'pandas',
              'python_dateutil',
              'pytz']
)

