# encoding: utf-8
"""
    drive.fs.fat32.__init__
    ~~~~~~~~~~~~~~~~~~~~~~

    This module implements the routine functions of creation of FAT32 objects.
"""
from drive.types import register
from .structs import FAT32
from drive.keys import *
import os
import matplotlib.pyplot as plt

__all__ = ['get_fat32_obj', 'get_fat32_partition']


@register(k_FAT32)
def get_fat32_obj(entry, stream, ui_handler=None):
    """Create FAT32 object according to a partition entry.

    :param entry: the entry used to locate the partition.
    :param stream: stream to parse against.
    """
    first_byte_addr = entry[k_first_byte_address]

    stream.seek(first_byte_addr, os.SEEK_SET)

    return FAT32(stream, preceding_bytes=first_byte_addr, ui_handler=ui_handler)


def get_fat32_partition(stream):
    """Create FAT32 object from the very beginning position of the stream,
    useful for reading partition streams instead of hard disk streams.

    :param stream: stream to parse against.
    """
    return FAT32(stream, preceding_bytes=0)


def first_clusters_of_fat32(entries):
    """Get the first cluster numbers of the entries representing an FAT32
    partition.

    :param entries: entries to get first clusters from.
    """

    return entries['first_cluster'].tolist()


def last_clusters_of_fat32(entries):
    """Get the last cluster numbers of the entries representing an FAT32
    partition.

    :param entries: entries to get last clusters from.
    """

    return map(lambda l: l[-1][-1], entries['cluster_list'].tolist())


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

    for _, (_, obj) in enumerate(entries.iterrows()):
        i = obj.id

        x.append(i)

        if plot_first_cluster:
            y_prime.append(obj.first_cluster)

        if plot_average_cluster:
            y.append(obj.avg_cluster)
            y_err[0].append(y[-1] - obj.cluster_list[0][0])
            y_err[1].append(obj.cluster_list[-1][-1] - y[-1])

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
        ax.errorbar(x, y, yerr=y_err, fmt='-o', label='avg cluster')
    if plot_first_cluster:
        ax.plot(x, y_prime, 'gx',
                 linestyle='dashed', label='first cluster')
    ax.legend()
    ax.set_xlabel('文件编号')
    ax.set_ylabel('簇号')

    if show:
        plt.show(figure)

    return figure
