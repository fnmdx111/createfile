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

    partitions = (get_partition_obj(entry, stream)
                  for entry in mbr[k_PartitionEntries])

    return partitions


if __name__ == '__main__':
    with ImageStream('d:/edt.raw') as f:
        partitions = get_drive_obj(f)
