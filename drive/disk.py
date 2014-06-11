# encoding: utf-8

from .keys import *
from .boot_sector import ClassicalMBR
from stream import ImageStream
from .types import registry


def get_drive_obj(stream):
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



if __name__ == '__main__':
    with ImageStream('d:/edt.raw') as f:
        partitions = get_drive_obj(f)
