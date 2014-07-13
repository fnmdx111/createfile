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
