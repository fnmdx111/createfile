
Statistical Metrics for createfile
====

This module makes use of normalized Kendall's tau score and Spearman's rho
score to help analyzing the relation between first cluster and creation
timestamp of the files.

Introduction to the `stats` API
----
The `stats` package contains mainly 3 parts, which are calculation,
validation and plotting.

Calculation is done through function `calc_windowed_metrics`, which takes
* a list of functions to calculate the metrics;
* a DataFrame containing the entries;
* some other less important parameters

and returns a list containing all the metrics calculated. If everything goes
well the returned object is a two-dimension list.

Validation is done through function `validate_metrics`, which takes
* a list of metrics (the return value of `calc_windowed_metrics` would be
just fine);
* a list of value domains of the function used in calculation;
* a list of sizes of rectangles (or box, if you like);
* a list of thresholds

and returns three arrays: normality data (or array, if you like), abnormality
data and background line data.

Plotting is done through function `plot_windowed_metrics`, which takes
* normality array, abnormality array and background line array;
* a list of the names of the legend;
* a list of format string to do some style setting for the plots.

And finally, use `matplotlib.pyplot.show()` to show all the plots. Note that
each time you call `plot_windowed_metrics` it automatically generates a new
figure object to plot on.

For example, see section Run.


Dependency
----
This module now depends on the following libraries:
* scipy, which provides `scipy.stats.rankdata`
* numpy
* matplotlib

To compile the speedup module from source, you need cython.

Run
----
This module provides one single function `plot_windowed_metrics` which
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

