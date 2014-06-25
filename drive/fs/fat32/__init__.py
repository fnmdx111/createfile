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
try:
    import prettyplotlib as ppl
except ImportError:
    ppl = plt

__all__ = ['get_fat32_obj', 'get_fat32_partition']


@register(k_FAT32)
def get_fat32_obj(entry, stream):
    """Create FAT32 object according to a partition entry.

    :param entry: the entry used to locate the partition.
    :param stream: stream to parse against.
    """
    first_byte_addr = entry[k_first_byte_address]

    stream.seek(first_byte_addr, os.SEEK_SET)

    return FAT32(stream, preceding_bytes=first_byte_addr)


def get_fat32_partition(stream):
    """Create FAT32 object from the starting position of the stream, useful for
    partition streams instead of hard disk streams.

    :param stream: stream to parse against.
    """
    return FAT32(stream, preceding_bytes=0)


def plot_fat32(entries):
    """Plot the status of the entries with matplotlib. You may want to filter
    the entries according to your will before call this function.

    :param entries: entries to plot against.
    """

    # TODO use date time as x coordinates
    x, y, y_prime, y_err = [], [], [], [[], []],

    for i, (_, obj) in enumerate(entries.iterrows()):
        x.append(i)

        y.append(obj.avg_cluster)
        y_prime.append(obj.first_cluster)

        y_err[0].append(y[-1] - obj.cluster_list[0][0])
        y_err[1].append(obj.cluster_list[-1][-1] - y[-1])

    # there isn't error bar support in prettyplotlib
    plt.errorbar(x, y, yerr=y_err, fmt='-o', label='avg cluster')
    plt.plot(x, y_prime, 'gx', linestyle='dashed', label='first cluster')
    ppl.legend()

    plt.show()

