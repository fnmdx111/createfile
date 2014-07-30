# encoding: utf-8
"""
    drive.fs.fat32.__init__
    ~~~~~~~~~~~~~~~~~~~~~~

    This module implements the routine functions of creation of FAT32 objects.
"""
import os

from drive.types import register
from .structs import FAT32
from drive.keys import *


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
