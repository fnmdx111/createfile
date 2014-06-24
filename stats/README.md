
Statistical Metrics for createfile
====

This module makes use of normalized Kendall's tau score and Spearman's rho
score to help analyzing the relation between first cluster and creation
timestamp of the files.

Dependency
----
This module now depends on the following libraries:
* scipy, which provides `scipy.stats.rankdata`
* numpy
* matplotlib

For better color scheme of the plots, you need prettyplotlib. If
prettyplotlib is not installed, it will simply fallback to the old
matplotlib color scheme.

To compile the speedup module from source, you need cython.

Run
----
This module provides one single function `get_windowed_metrics` which
takes a list of functions which calculate the desired metrics and uses
matplotlib to plot.

An example is
[here](https://gist.github.com/mad4alcohol/491033b9ba3b43b6551f ) on gist
and ready to use (FAT32 only).

Known Issues
----
Due to a virtualenv bug, `matplotlib.pyplot.show` has trouble functioning
under a virtualenv on Windows. To temporarily solve this, see this
[post](https://github.com/pypa/virtualenv/issues/93 ).

