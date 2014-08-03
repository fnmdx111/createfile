# encoding: utf-8
import matplotlib.pyplot as plt


def plot_fat32(entries,
               figure=None, subplot_n=111,
               log_info=True, logger=None,
               plot_average_cluster=True,
               plot_first_cluster=True,
               show=False):
    """Plot the status of the entries with matplotlib. You may want to filter
    the entries according to your will before call this function.

    :param entries: entries to plot against.
    :param figure: optional, a figure object to plot on.
    :param subplot_n: optional, subplot number.
    :param log_info: optional, whether to log file information during preparing
                     the plot.
    :param plot_average_cluster: optional, plot average cluster.
    :param plot_first_cluster: optional, plot first cluster.
    :param show: whether showing the graph after plotting.
    """

    x, y, y_prime, y_err = [], [], [], [[], []],

    _p = logger.info if logger else print

    for _i, (_, obj) in enumerate(entries.iterrows()):
        i = _i

        x.append(i)

        if plot_first_cluster:
            y_prime.append(obj.first_cluster)

        if plot_average_cluster:
            y.append(obj.avg_cluster)

            min_cluster = min(map(lambda x: min(*x), obj.cluster_list))
            max_cluster = max(map(lambda x: max(*x), obj.cluster_list))

            y_err[0].append(y[-1] - min_cluster)
            y_err[1].append(max_cluster - y[-1])

        if log_info:
            _p('found FDT entry %s:\n'
               '\tfp: %s\n'
               '\tfc: %s\tac: %s\toc: %s\n'
               '\tcr: %s\n'
               '\tmd: %s\n' % (i,
                               obj.full_path,
                               obj.first_cluster,
                               obj.avg_cluster,
                               sum(e - s + 1 for s, e in obj.cluster_list),
                               obj.create_time,
                               obj.modify_time))

    figure = figure or plt.figure()
    ax = figure.add_subplot(subplot_n)

    if plot_average_cluster:
        # there isn't error bar support in prettyplotlib
        ax.errorbar(x, y, yerr=y_err, fmt='-o', label='平均簇号')
    if plot_first_cluster:
        ax.plot(x, y_prime, 'gx',
                 linestyle='dashed', label='首簇号')
    ax.legend()
    ax.set_xlabel('编号')
    ax.set_ylabel('簇号')

    if show:
        plt.show(figure)

    return figure
