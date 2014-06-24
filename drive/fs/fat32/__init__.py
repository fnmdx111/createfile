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
