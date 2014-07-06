# encoding: utf-8
"""
    drive.disk
    ~~~~~~~~~~

    This module implements :func:`get_drive_obj` which parses the given stream to
    :class:`Partition` objects.
"""

from .keys import *
from .boot_sector import ClassicalMBR
from .types import registry


def get_drive_obj(stream):
    """Parse the given stream as a whole hard drive.

    :param stream: the stream containing the bytes of the hard drive.
    """

    mbr = ClassicalMBR.parse_stream(stream)

    def get_partition_obj(partition_entry, stream):
        return registry[partition_entry[k_partition_type]](partition_entry,
                                                           stream)

    for entry in mbr[k_PartitionEntries]:
        if entry[k_partition_type] == k_ignored:
            continue

        p = get_partition_obj(entry, stream)
        if entry[k_partition_type] == k_ExtendedPartition:
            for partition in p:
                yield partition
        else:
            yield p
