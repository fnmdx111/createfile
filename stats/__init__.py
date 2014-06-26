# encoding: utf-8
"""
    stats.__init__
    ~~~~~~~~~~~~~~

    This module implements the :func:`get_windowed_metrics` function which is
    the only public interface of this package.
"""
from stats.misc import windowed
import numpy as np
import matplotlib.pyplot as plt


__all__ = ['get_windowed_metrics']


def plot_windowed_metrics(fs, entries,
                          figure=None, subplot_n=111,
                          fn=None, echo=True, show=False,
                          window_size=5,
                          window_step=1):
    """Calculates metrics within the sliding windows. You may want to clean your
    DataFrame first.

    :param fs: a list of functions used to calculate the metrics.
    :param entries: a pandas `DataFrame` object containing all the file
                    entries.
    :param figure: optional, a figure object to plot on.
    :param subplot_n: optional, subplot number.
    :param fn: optional, the function's names.
    :param echo: optional, if true, window information is printed.
    :param show: optional, if true, the plot will be shown.
    :param window_size: optional, the size of the windows.
    :param window_step: optional, the step between the windows.
    """

    fn = fn or [f.__name__ for f in fs]

    # values ::= [[f1_0, f1_1, f1_2, ..., f1_n],
    #             [f2_0, f2_1, f2_2, ..., f2_n],
    #             ...,
    #             [fn_0, fn_1, fn_2, ..., fn_n]]
    w_cnt, values = 0, [[] for _ in fs]
    for w in windowed(list(entries.iterrows()),
                      size=window_size,
                      step=window_step):
        w = tuple(w)

        for i, f in enumerate(fs):
            # calculate each metric according to `fs`
            v = f(np.array(list(map(lambda x: x[1].first_cluster,
                                    w))),
                  np.array(list(map(lambda x: x[1].create_time
                  # timestamps are multiplied by 1000 so that they are integers
                                                  .timestamp() * 1000,
                                    w))))
            values[i].append(v)

        if echo:
            print('window %s:' % w_cnt)
            # this will form the following format string according to
            # `window_size`:
            # '{0[0]}\n\t{0[1]}\n'
            # '{1[0]}\n\t{1[1]}\n'
            # '{...[0]}\n\t{...[1]}\n'
            # '{n[0]}\n\t{n[1]}'
            print('\n'.join('{{{0}[0]}}\n\t{{{0}[1]}}'.format(_)
                            for _ in range(len(w)))
                  .format(*map(lambda x: (x[1].full_path,
                                          x[1].first_cluster),
                               w)))
            for n, v in zip(fn, values):
                # print the metrics with their names
                print('%s: %s' % (n, v[w_cnt]))
            print('----------------')

        w_cnt += 1

    figure = figure or plt.figure()
    ax = figure.add_subplot(subplot_n)

    plots = []
    for n, v in zip(fn, values):
        plots.append(ax.plot(range(w_cnt), v, 'D-',
                             label=n)[0])
    ax.legend(plots, fn)

    if show:
        plt.show(figure)

    return values
