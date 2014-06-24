# encoding: utf-8
"""
    drive.fs.ntfs.structs
    ~~~~~~~~~~~~~~~~~~~~~

    This module implements the structs used when parsing NTFS partition and class
    :class:`NTFS`.
"""
from functools import partial
from io import BytesIO
import os
from construct import Struct, Bytes, String, ULInt16, ULInt8, ULInt64, SLInt8,\
    Magic, Value, ULInt32
from drive.fs import Partition
from .attributes import attributes
from .misc import StrictlyUnused, Unused
from drive.keys import *
from misc import MAGIC_END_SECTION
from stream.auxiliary import NTFSClusterStream


def _sl_int8_entry(c, key):
    """Calculate certain entry values specially.

    :param c: the context object.
    :param key: the key of the value to be calculated.
    """

    val = c[key]

    if val < 0:
        return 2 ** (-1 * val)
    else:
        bytes_per_sector = c[k_bytes_per_sector]
        sectors_per_cluster = c[k_sectors_per_cluster]
        bytes_per_cluster = bytes_per_sector * sectors_per_cluster

        return val * bytes_per_cluster

NTFSBootSector = Struct(k_NTFSBootSector,
    Bytes           (k_jump_instruction, 3),
    String          (k_OEM_name, 8),
    ULInt16         (k_bytes_per_sector),
    ULInt8          (k_sectors_per_cluster),
    ULInt16         (k_number_of_reserved_sectors),
    StrictlyUnused  (5),
    ULInt8          (k_media_descriptor),
    StrictlyUnused  (2),
    Unused          (2), # sectors per track
    Unused          (2), # number of heads
    Unused          (4), # hidden sectors
    StrictlyUnused  (4),
    Unused          (4),
    ULInt64         (k_number_of_sectors),
    ULInt64         (k_cluster_number_of_MFT_start),
    ULInt64         (k_cluster_number_of_MFT_mirror_start),
    SLInt8          (k_clusters_per_MFT_record),
    Value           (k_bytes_per_MFT_record,
                     partial(_sl_int8_entry, key=k_clusters_per_MFT_record)),
    Unused          (3),
    SLInt8          (k_clusters_per_index_record),
    Value           (k_bytes_per_index_record,
                     partial(_sl_int8_entry, key=k_clusters_per_index_record)),
    Unused          (3),
    Bytes           (k_serial_number, 8),
    Unused          (4), # checksum
    Bytes           (None, 0x1aa), # bootstrap code
    Magic           (MAGIC_END_SECTION)
)

FileRecordHeader = Struct(k_FileRecordHeader,
    ULInt16(k_offset_to_update_sequence),
    ULInt16(k_size_of_update_sequence),
    ULInt64(k_logfile_sequence_number),
    ULInt16(k_sequence_number), # WinHex denotes this as `use/deletion count'
    Unused (2), # hard link count
    ULInt16(k_offset_to_first_attribute),
    ULInt16(k_flags), # 0x00 - deleted file,
                      # 0x01 - file,
                      # 0x02 - deleted directory,
                      # 0x03 - directory
    ULInt32(k_logical_size),
    ULInt32(k_allocated_size),
    ULInt64(k_base_record_index),
    ULInt16(k_id_of_next_attribute),
    Unused (2),
    ULInt32(k_number_of_this_record),
)


class MFTRecord:
    """
    Class which represents MFT records.
    """
    def __init__(self, parent, stream):
        """
        :param parent: the partition which this MFT record resides on.
        :param stream: a `BytesIO` object which contains the MFT record. Since
                       we've already had the size of an MFT record from boot
                       sector, this can be easily done.
        """

        self.stop = False

        assert isinstance(stream, BytesIO)
        self.stream = stream
        self.parent = parent

        self.attributes = {}

        signature = stream.read(4)
        if signature != b'FILE' and signature != b'BAAD':
            self.stop = True
            return

        {b'FILE': self.do_file,
         b'BAAD': self.do_bad}[signature]()

    def do_file(self):
        """Parse `FILE` records."""

        header = FileRecordHeader.parse_stream(self.stream)
        self.stream.seek(header[k_offset_to_update_sequence])
        update_seq = self.stream.read(header[k_size_of_update_sequence] * 2)

        ntfs_stream = NTFSClusterStream(self.stream.getvalue(),
                                        self.parent.bytes_per_sector,
                                        update_seq)

        ntfs_stream.seek(header[k_offset_to_first_attribute])
        for attribute in attributes(ntfs_stream):
            # this may not be appropriate, there are times that multiple
            # instances of attributes of the same type exist
            # what are the relationships between them?
            self.attributes[attribute.type] = attribute

    def do_bad(self):
        """Parse `BAAD` records, which are simply ignored."""

        pass


class NTFS(Partition):
    """
    Class that represents NTFS partitions.
    """
    type = 'NTFS'

    def __init__(self, stream, preceding_bytes):
        """
        :param stream: the stream to parse.
        :param preceding_bytes: bytes preceding this partition.
        """

        super(NTFS, self).__init__(self.type, stream, preceding_bytes,
                                   lambda s: NTFSBootSector.parse_stream(s))

        self.bytes_per_sector = self.boot_sector[k_bytes_per_sector]
        self.bytes_per_cluster = (self.boot_sector[k_sectors_per_cluster] *
                                  self.bytes_per_sector)
        self.bytes_per_mft_record = self.boot_sector[k_bytes_per_MFT_record]
        self.logger.info('read boot sector, bytes per sector is %d, '
                         'bytes per cluster is %d, '
                         'bytes per MFT record is %d',
                         self.bytes_per_sector, self.bytes_per_cluster,
                         self.bytes_per_mft_record)

        mft_abs_pos = self.abs_lcn2b(
            self.boot_sector[k_cluster_number_of_MFT_start])
        stream.seek(mft_abs_pos, os.SEEK_SET)
        self.logger.info('stream jumped to %s and ready to read MFT records',
                         hex(mft_abs_pos))
        self.mft_records = []

    def get_mft_records(self):
        """Parse the MFT records residing on this partition."""

        self.mft_records = list(iter(self))
        self.logger.info('read %s mft record(s)' % len(self.mft_records))

    def __iter__(self):
        """Implement iterator protocol for pythonicness."""

        while True:
            record = MFTRecord(self,
                               BytesIO(self.stream.read(
                                   self.bytes_per_mft_record)))
            if record.stop:
                break
            yield record

    def lcn2b(self, lcn):
        """Convert logical cluster number to offset in bytes.

        :param lcn: logical cluster number.
        """

        return self.bytes_per_cluster * lcn

    def abs_lcn2b(self, lcn):
        """Convert logical cluster number to offset relative to the hard disk
        in bytes, i.e. absolute offset.

        :param lcn: logical cluster number.
        """

        return self.lcn2b(lcn) + self.preceding_bytes
