# encoding: utf-8
from ..keys import k_ignored, k_ExtendedPartition, k_FAT32, k_NTFS

supported_partition_types = {
            0x0: k_ignored,
            0x5: k_ExtendedPartition,
            0xf: k_ExtendedPartition,
            0xb: k_FAT32,
            0xc: k_FAT32,
            0x7: k_NTFS,
}
