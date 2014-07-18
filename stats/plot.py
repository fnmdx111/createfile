# encoding: utf-8
import matplotlib.pyplot as plt


def plot_windowed_metrics(normal_data, abnormal_data,
                          line_data, fn, dot_formats,
                          plot_normal=None,
                          plot_abnormal=None,
                          figure=None, subplot_n=111,
                          show=False):
    """Plot metrics values. You may want to clean your
    DataFrame first.

    :param normal_data: normal data ([[[x_n], [y_n]], [[a_n], [b_n]]]).
    :param abnormal_data: abnormal data.
    :param line_data: data that represents the background line.
    :param fn: metric names used in legend.
    :param dot_formats: dot format string used in plots, the format string for
                        each metric is given in the order of normal dot format,
                        abnormal dot format and line format. E.g.
                        ['Dx--', '^v-'].
    :param plot_normal: optional, if true, plot normal dots.
    :param plot_abnormal: optional, if true, plot abnormal dots.
    :param figure: optional, a figure object to plot on.
    :param subplot_n: optional, subplot number.
    :param show: optional, if true, the plot will be shown.
    """

    figure = figure or plt.figure()
    ax = figure.add_subplot(subplot_n)

    plot_normal = plot_normal or [True for _ in fn]
    plot_abnormal = plot_abnormal or [True for _ in plot_normal]

    plots, names = [], []
    for n, vs, fmt, pn, pa in zip(fn,
                                  zip(line_data, normal_data, abnormal_data),
                                  dot_formats,
                                  plot_normal,
                                  plot_abnormal):

        # plot background line
        names.append(n)
        plots.append(ax.plot(vs[0][0], vs[0][1], fmt[2:],
                             label=names[-1])[0])
        if pn:
            # plot normal dots
            names.append('%s - %s' % (n, 'normal'))

            plots.append(ax.plot(vs[1][0], vs[1][1], 'g%s' % fmt[0],
                                 label=names[-1])[0])
        if pa:
            # plot abnormal dots
            names.append('%s - %s' % (n, 'abnormal'))

            plots.append(ax.plot(vs[2][0], vs[2][1], 'r%s' % fmt[1],
                                 label=names[-1])[0])
    ax.legend(plots, names)

    if show:
        plt.show(figure)

    return figure
