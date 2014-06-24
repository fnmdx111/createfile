# encoding: utf-8
"""
    stats.speedup.alg
    ~~~~~~~~~~~~~~~~~

    This is a cython module, which implements the two function for calculating
    the metrics - Kendall's tau score and Spearman's rho score.
"""
from __future__ import division
# this line is necessary, it import the numpy library into current namespace
import numpy as np
# this line is necessary, it import the numpy compile-time information into
# current namespace
cimport numpy as np

try:
    # try import scipy.stats.rankdata, if it's not there, fallback to the slower
    # one which is provided by numpy
    from scipy.stats import rankdata as rd
except ImportError:
    rd = lambda arr: map(lambda i: np.float64(i),
                         np.searchsorted(np.sort(arr), arr))

cpdef u_tau(np.ndarray arr1, np.ndarray arr2):
    """Kendall's tau score.

    :param arr1, arr2: two np.ndarray to be calculated with.
    """

    cdef np.ndarray[np.float64_t] rk1 = rd(arr1)
    cdef np.ndarray[np.float64_t] rk2 = rd(arr2)

    cdef int l = rk1.shape[0]
    cdef unsigned int sum_ = 0
    for i from 0 <= i < l:
        if rk1[i] < rk2[i]:
            sum_ += 1

    cdef np.float64_t ret = sum_ / (l * (l - 1) >> 1)
    return ret


cpdef u_rho(np.ndarray arr1, np.ndarray arr2):
    """Spearman's rho score.

    :param arr1, arr2: two np.ndarray to be calculated with.
    """

    cdef np.ndarray[np.float64_t] rk1 = rd(arr1)
    cdef np.ndarray[np.float64_t] rk2 = rd(arr2)

    cdef int l = rk1.shape[0]
    cdef np.float64_t sum_ = 0
    cdef np.float64_t x = 0.
    for i from 0 <= i < l:
        x = rk1[i] - rk2[i]
        sum_ += x * x

    cdef np.float64_t ret = 1 - (sum_ * 6) / (l * (l * l - 1))
    return ret
