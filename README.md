
Apollō (code name createfile)
====

Deploy
----
Download [`bundle.7z`](https://www.dropbox.com/s/gxdtzjc49tkzf2i/bundle.7z )
and extract it into anywhere you like.
Make sure you have Python3 installed. If not, go to
[www.python.org](https://www.python.org/ ) and download the latest version
of Python __x64__.
Then read `README.md` in `bundle.7z`.

Build
----
This is a Python project, which is not generally involved with building.
However, this very project comes with a few Cython modules, which needs
building from source. Though the compiled `pyd` files of `x64` version are
included in the source already, you can compile the `pyx` sources if you
want the ones of `x86` version.

To build the project from source, make sure you have all the dependencies
and Visual Studio 2010 (MinGW is ok to go, I think, after some tedious hacking),
then simply run

    python setup.py build

and look into the build/lib.xxx folder.


How to run
----
First activate the virtualenv we created earlier, using

    path/to/your/env/Scripts/activate.bat

or if you prefer POSIX terminals

    source path/to/your/env/Scripts/activate

Then under project root directory, run

    python bootstrap.py

to load the GUI. If you dislike the cmd window, rename `bootstrap.py` to
`bootstrap.pyw` and run

    python bootstrap.pyw


Minimal dependencies
----

* scipy (mainly used in stats)
* numpy (dependency of various libraries)
* matplotlib (used in plotting)
* pyparsing (dependency of matplotlib)
* PySide (for gui)
* Jinja2 (for timeline template rendering)
* MarkupSafe (dependency of Jinja2)
* construct (mainly used in package drive for binary parsing)
* PyWin32 (mainly used in streaming physical drive)
* pandas (mainly used in encapsulating file entries of partitions)
* python-dateutil (dependency of pandas)
* pytz (dependency of pandas)
* six (library providing compatibility, dependency of various libraries)
* Cython (optional, used for compiling speed-up modules for various packages)

About 160MB in a 7z archive.


Thanks
----
The NTFS driver in package `drive.fs.ntfs` utilizes the project
[INDXParse](https://github.com/williballenthin/INDXParse ) from Willi Ballenthin.

**Thanks a lot.**


Benchmark
----
Following is a vague benchmark:
* NTFS: parsing 205052 MFT records on a 678GB external hard drive (total 931GB)
costs about 21m46s. I.e. about 10k MFT records per minute, about 30GB per minute.

To get a benchmark yourself, check out module `test.benchmark`.


Licensing
====

Licenced under GNU LGPLv3 (perhaps).

