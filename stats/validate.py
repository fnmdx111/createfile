# encoding: utf-8
"""
    stats.validate
    ~~~~~~~~~~~~~~

    This module implements the basic box-shaped abnormality detection or
    (validation).
"""
from functools import partial
from .misc import segmented

Abnormal = False
Normal = True


def _check_series(id_, series,
                  rect_size=(5, 5),
                  y_ext=(-1, 1),
                  count_threshold=1,
                  check_clusters=False):
    """Check if any point in the given series agrees with the given box.

    :param id_: list of id of the entries of the points.
    :param series: the series of points to check.
    :param rect_size: box (or rectangle) size, (width, height).
    :param y_ext: extreme values of the y axis or (value domain if you like).
    :param count_threshold: threshold of count of adjacent points in the given
                            box, if the count is less than the threshold, then
                            the point is an abnormality.
    """
    canonicalize = lambda _: _[0] if check_clusters else _

    y_min, y_max = y_ext

    # it's not important if y values are integers or not
    sh = rect_size[1] / 2
    for (x, y), (segment_x, segment_y) in segmented(series,
                                                    width=rect_size[0],
                                                    strict=False):
        if check_clusters:
            yl, yh = y
        else:
            yl = yh = y
        _y_min, _y_max = max(y_min, yl - sh), min(y_max, yh + sh)

        _count = 0
        for sx, sy in zip(segment_x, segment_y):
            if sx != x:
                if check_clusters:
                    if (_y_min <= sy[0] <= _y_max
                     or _y_min <= sy[1] <= _y_max):
                        _count += 1
                else:
                    if _y_min <= sy <= _y_max:
                        _count += 1

        canonical_y = canonicalize(y)

        if _count < count_threshold:
            yield Abnormal, (id_[x], canonical_y)
        else:
            yield Normal, (id_[x], canonical_y)


def validate_metrics(ids, metrics,
                     value_domains,
                     rect_sizes,
                     count_thresholds,
                     check_clusters=False):
    """Validate the metrics and detects abnormalities.

    :param ids: id of the entries of the metrics.
    :param metrics: metrics to validate.
    :param value_domains: value domains of the functions used in calculating the
                         metrics.
    :param rect_sizes: rectangle sizes for each metric.
    :param count_thresholds: count thresholds for each metric.
    :param check_clusters: if true, a special box-shaped validation will be
                           applied.
    """

    normal, abnormal, line = [], [], []
    for id_, series, y_ext, rect_size, count_threshold in zip(ids,
                                                              metrics,
                                                              value_domains,
                                                              rect_sizes,
                                                              count_thresholds):
        normal.append([[], []])
        abnormal.append([[], []])
        line.append([[], []])

        for status, (x, y) in _check_series(id_, series,
                                            rect_size=rect_size,
                                            y_ext=y_ext,
                                            count_threshold=count_threshold,
                                            check_clusters=check_clusters):
            line[-1][0].append(x)
            line[-1][1].append(y)
            if status == Normal:
                normal[-1][0].append(x)
                normal[-1][1].append(y)
            elif status == Abnormal:
                abnormal[-1][0].append(x)
                abnormal[-1][1].append(y)

    return normal, abnormal, line

validate_clusters = partial(validate_metrics, check_clusters=True)
