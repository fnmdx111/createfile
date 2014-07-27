# encoding: utf-8
"""
    drive.fs.ntfs.__init__
    ~~~~~~~~~~~~~~~~~~~~~~

    This module implements the routine functions of creation of NTFS objects.
"""
import os
from .structs import NTFS
from drive.keys import *
from drive.types import register
import matplotlib.pyplot as plt

__all__ = ['get_ntfs_obj', 'get_ntfs_partition']

@register(k_NTFS)
def get_ntfs_obj(entry, stream, ui_handler=None):
    """Create NTFS object according to a partition entry.

    :param entry: the entry used to locate the partition.
    :param stream: stream to parse against.
    """

    first_byte_addr = entry[k_first_byte_address]

    stream.seek(first_byte_addr, os.SEEK_SET)

    return NTFS(stream, preceding_bytes=first_byte_addr, ui_handler=ui_handler)


def get_ntfs_partition(stream):
    """Create NTFS object from the starting position of the stream, useful for
    partition streams instead of hard disk streams.

    :param stream: stream to parse against.
    """

    return NTFS(stream, preceding_bytes=0)

def plot_sne1(entries,
              figure=None, subplot_n=111,
              log_info=False, logger=None,
              y_attr='si_create_time', y_attr_name='$SI创建时间',
              show=False):
    entries = entries[entries.sn == 1].sort(columns=['id'])

    _p = logger.info if logger else print

    xs, ys = [], []
    for _, o in entries.iterrows():
        xs.append(o.id)
        ys.append(o[y_attr])

        if log_info:
            pass

    figure = figure or plt.figure()
    ax = figure.add_subplot(subplot_n)

    ax.plot(xs, ys, 'cD', linestyle='-.', label=y_attr_name)

    ax.legend()
    ax.set_xlabel('MFT编号')
    ax.set_ylabel(y_attr_name)

    if show:
        plt.show(figure)

    return figure

def plot_lsn(entries,
             figure=None, subplot_n=111,
             log_info=False,
             logger=None,
             y_attr='si_create_time', y_attr_name='$SI创建时间',
             show=False):
    entries = entries.sort(columns=['lsn', 'id'])

    _p = logger.info if logger else print

    xs, ys = [], []
    for _, o in entries.iterrows():
        xs.append(o.lsn)
        ys.append(o[y_attr])

        if log_info:
            pass

    figure = figure or plt.figure()
    ax = figure.add_subplot(subplot_n)

    ax.plot(xs, ys, 'b^', linestyle='-.', label=y_attr_name)

    ax.legend()
    ax.set_xlabel('$LogFile序列号')
    ax.set_ylabel(y_attr_name)

    if show:
        plt.show(figure)

    return figure
