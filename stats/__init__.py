# encoding: utf-8
"""
    stats.__init__
    ~~~~~~~~~~~~~~

    This module implements the :func:`get_windowed_metrics` function which is
    the only public interface of this package.
"""
from collections import Counter
import datetime as dt

import numpy as np
from drive.fs.ntfs.indxparse.misc import parse_error_datetime_stub

from .misc import windowed, segmented
from .validate import validate_metrics
from .plot import plot_windowed_metrics
from drive.fs.fat32 import FAT32
from drive.fs.ntfs import NTFS


__all__ = ['plot_windowed_metrics',
           'calc_windowed_metrics',
           'validate_metrics']


def calc_windowed_metrics(fs, entries,
                          fn=None, echo=True, logger=None,
                          attr1=lambda x: x.create_time.timestamp(),
                          attr2=lambda x: x.first_cluster,
                          log_fmt='{{{0}.full_path}}\n\t{{{0}.first_cluster}}\t'
                                  '{{{0}.create_time}}',
                          window_size=5, window_step=1):
    """Calculate metrics within given window. You may want to clean your
    DataFrame first.

    :param fs: a list of functions used to calculate the metrics.
    :param entries: a pandas `DataFrame` object containing all the file
                    entries.
    :param fn: optional, the function's names.
    :param echo: optional, if true, window information is printed.
    :param log_fmt: optional, format string for file information logging, please
                    follow the default value as an example when customizing this
                    parameter.
    :param window_size: optional, the size of the windows.
    :param window_step: optional, the step between the windows.
    """

    fn = fn or [f.__name__ for f in fs]
    _p = logger.info if logger else print

    # values ::= [[f1_0, f1_1, f1_2, ..., f1_n],
    #             [f2_0, f2_1, f2_2, ..., f2_n],
    #             ...,
    #             [fn_0, fn_1, fn_2, ..., fn_n]]
    w_cnt, xs, values = 0, [[] for _ in fs], [[] for _ in fs]
    for w in windowed(list(entries.iterrows()),
                      size=window_size,
                      step=window_step):
        w = tuple(w)

        for i, f in enumerate(fs):
            # calculate each metric according to `fs`
            v = f(np.array(list(map(lambda x: attr1(x[1]),
                                    w))),
                  np.array(list(map(lambda x: attr2(x[1]),
                  # timestamps are multiplied by 1000 so that they are integers
                                    w))))
            values[i].append(v)
            xs[i].append(w[0][1].id)

        if echo:
            _p('window %s:' % w_cnt)
            # this will form the following format string according to
            # `window_size`
            _p('\n'.join(log_fmt.format(_) for _ in range(len(w)))
                  .format(*map(lambda x: x[1], w)))
            for n, v in zip(fn, values):
                # print the metrics with their names
                _p('%s: %s' % (n, v[w_cnt]))
            _p('----------------')

        w_cnt += 1

    return xs, values


def _dtf(row, attrs, days_counter):
    for t in map(lambda a: row[a], attrs):
        if t is parse_error_datetime_stub:
            continue

        days_counter[t.date()] += 1

        yield t


def _fat32_dtf(row, days_counter):
    time_attrs = ['create_time', 'modify_time', 'access_date']
    return _dtf(row, time_attrs, days_counter)


def _ntfs_dtf(row, days_counter):
    time_attrs = ['%s_%s_time' % (attr, name)
                  for attr in ['si', 'fn']
                  for name in ['create', 'modify', 'access', 'mft']]
    return _dtf(row, time_attrs, days_counter)


suffices = {'.exe', '.txt', '.pdf', '.jpg', '.rar', '.doc', '.png'}

def statistical_summary_of(type_, rules, entries):
    dtf = {FAT32.type: _fat32_dtf, NTFS.type: _ntfs_dtf}[type_]

    days_counter = Counter()
    file_type_counter = Counter()
    conclusion_counter = Counter()
    abnormal_counter = Counter()

    rules_category = {}

    for _, r in rules:
        rules_category[r.conclusion] = r.abnormal

    min_st, max_et = dt.datetime.max, dt.datetime.min
    for _, o in entries.iterrows():
        dts = list(dtf(o, days_counter))

        min_st = min(min_st, *dts)
        max_et = max(max_et, *dts)

        maybe_suffix = o.full_path[-4:]
        if maybe_suffix in suffices:
            file_type_counter[maybe_suffix] += 1

        for c in o.conclusions:
            conclusion_counter[c] += 1

        if o.abnormal:
            abnormal_counter[True] += 1
        else:
            abnormal_counter[False] += 1

    return ((min_st, max_et),
            days_counter,
            file_type_counter,
            conclusion_counter,
            abnormal_counter,
            rules_category)
