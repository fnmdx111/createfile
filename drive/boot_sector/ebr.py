# encoding: utf-8
import os
from drive.types import register, registry
from ..keys import *
from ._boot_sector import boot_sector_template


@register(k_ExtendedPartition)
def get_ext_partition_obj(entry, stream):
    first_byte_addr = entry[k_first_byte_address]
    while True:
        stream.seek(first_byte_addr, os.SEEK_SET)
        ebr = boot_sector_template(first_byte_addr).parse_stream(stream)

        real_entry, next_ebr_entry = ebr[k_PartitionEntries][:2]

        yield registry[real_entry[k_partition_type]](real_entry, stream)

        if next_ebr_entry[k_partition_type] == k_ignored:
            break
        first_byte_addr = next_ebr_entry[k_first_byte_address]

