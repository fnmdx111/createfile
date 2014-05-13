# encoding: utf-8
import os
from drive.fs.ntfs.structs import NTFS
from drive.keys import *

def get_ntfs_obj(entry, stream):
    first_byte_addr = entry[k_first_byte_address]

    stream.seek(first_byte_addr, os.SEEK_SET)

    return NTFS(stream, preceding_bytes=first_byte_addr)


def get_ntfs_partition(stream):
    return NTFS(stream, preceding_bytes=0)
