Speed-up of Cluster List Discovery of FAT32
====

Introduction
----
This package implements FAT32 cluster list discovery in Cython which speeds up
the process for about 22% (9.5s to 7.4s, the data set is an FAT32 partition with
the size of 8GB).

Normally this package contains a ready-to-use x64 pyd file for Python3.4
 (`_op.pyd`), however, if you choose to modify the source code (`_op.pxd`
which acts as header file and `_op.pyx` which acts as source file), you'll have
to do a re-compilation.

Compilation
----
Make sure you have Visual Studio 2010 and the latest version of Cython
installed. If not, run `pip install cython` to install Cython.

To compile the package, cd into `speedup`, run `python setup.py build_ext` and
copy the generated pyd file into `speedup`.

