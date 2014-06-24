# encoding: utf-8
from __future__ import division
import numpy as np
cimport numpy as np

try:
    from scipy.stats import rankdata as rd
except ImportError:
    rd = lambda arr: map(lambda i: np.float64(i),
                         np.searchsorted(np.sort(arr), arr))

cpdef u_tau(np.ndarray arr1, np.ndarray arr2):
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
