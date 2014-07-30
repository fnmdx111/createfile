# encoding: utf-8
"""
    drive.boot_sector.ebr
    ~~~~~~~~~~~~~~~~~~~~~

    This module implements the discovery of extended partitions.
"""
import os

from drive.types import register, registry
from ..keys import *
from ._boot_sector import boot_sector_template


@register(k_ExtendedPartition)
def get_ext_partition_obj(entry, stream):
    return _get_ext_partition_obj(
        entry, stream,
        lambda e, s: registry[e[k_partition_type]](e, s)
    )

def get_ext_partition_entries(entry, stream):
    return _get_ext_partition_obj(entry, stream, lambda _, __: _)

def _get_ext_partition_obj(entry, stream, f):
    """Get extended partitions.

    :param entry: entry representing the extended partitions.
    :param stream: stream to parse against.
    """

    first_byte_addr = entry[k_first_byte_address]
    while True:
        stream.seek(first_byte_addr, os.SEEK_SET)
        ebr = boot_sector_template(first_byte_addr).parse_stream(stream)

        real_entry, next_ebr_entry = ebr[k_PartitionEntries][:2]

        yield f(real_entry, stream)

        if next_ebr_entry[k_partition_type] == k_ignored:
            break
        first_byte_addr = next_ebr_entry[k_first_byte_address]

