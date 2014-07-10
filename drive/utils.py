# encoding: utf-8
import pywintypes
from .keys import k_PartitionEntries
from .boot_sector import ClassicalMBR
from stream import WindowsPhysicalDriveStream


def discover_physical_drives(rng=range(16)):
    available_drives = []
    for i in rng:
        try:
            _ = WindowsPhysicalDriveStream(i)
            available_drives.append(i)
        except pywintypes.error:
            continue

    return available_drives


def get_partition_table(stream):
    try:
        mbr = ClassicalMBR.parse_stream(stream)
        return mbr[k_PartitionEntries]
    except KeyError:
        # not a disk stream, may be a partition stream
        return []
