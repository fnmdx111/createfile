# encoding: utf-8
"""
    drive.fs.ntfs.structs
    ~~~~~~~~~~~~~~~~~~~~~

    This module implements the structs used when parsing NTFS partition and class
    :class:`NTFS`.
"""
import datetime
from functools import partial
from construct import Struct, Bytes, String, ULInt16, ULInt8, ULInt64, SLInt8,\
    Magic, Value
from pandas import DataFrame
from drive.fs import Partition
from .misc import StrictlyUnused, Unused
from .indxparse.MFT import MFTEnumerator, FixupBlock
from drive.keys import *
from misc import MAGIC_END_SECTION
from stream.auxiliary import MFTStream


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


class NTFS(Partition):
    """
    Class that represents NTFS partitions.
    """
    type = 'NTFS'

    __mft_attr__ = ['lsn', 'sn',
                    'si_create_time', 'si_modify_time',
                    'si_access_time', 'si_mft_time',
                    'fn_create_time', 'fn_modify_time',
                    'fn_access_time', 'fn_mft_time',
                    'first_cluster', 'cluster_list',
                    'full_path',
                    'is_directory', 'is_deleted',
                    'id']

    def __init__(self, stream, preceding_bytes, ui_handler=None):
        """
        :param stream: the stream to parse.
        :param preceding_bytes: bytes preceding this partition.
        """

        super(NTFS, self).__init__(self.type, stream, preceding_bytes,
                                   lambda s: NTFSBootSector.parse_stream(s),
                                   ui_handler=ui_handler)

        self.bytes_per_sector = self.boot_sector[k_bytes_per_sector]
        FixupBlock.set_sector_size(self.bytes_per_sector)

        self.bytes_per_cluster = (self.boot_sector[k_sectors_per_cluster] *
                                  self.bytes_per_sector)
        self.bytes_per_mft_record = self.boot_sector[k_bytes_per_MFT_record]
        self.logger.info('read boot sector, bytes per sector is %d, '
                         'bytes per cluster is %d, '
                         'bytes per MFT record is %d',
                         self.bytes_per_sector, self.bytes_per_cluster,
                         self.bytes_per_mft_record)

        self.mft_abs_pos = self.abs_lcn2b(
            self.boot_sector[k_cluster_number_of_MFT_start])
        # stream.seek(mft_abs_pos, os.SEEK_SET)
        self.logger.info('stream jumped to %s and ready to read MFT records',
                         hex(self.mft_abs_pos))

    def get_mft_records(self):
        """Parse the MFT records residing on this partition."""

        self.mft_records = list(iter(self))
        self.logger.info('read %s mft record(s)' % len(self.mft_records))

        return self.mft_records

    @staticmethod
    def runs_to_cluster_list(runs):
        cluster_list = []
        current_offset = 0
        for offset, length in runs:
            current_offset += offset
            cluster_list.append([current_offset, current_offset + length - 1])

        return cluster_list

    def __iter__(self):
        """Implement iterator protocol for pythonicness."""
        mft_enumerator = MFTEnumerator(self,
                                       MFTStream(self.stream,
                                                 self.mft_abs_pos,
                                                 self.bytes_per_mft_record))
        for id_, (record, record_path) in enumerate(
                mft_enumerator.enumerate_paths()
        ):
            si = record.standard_information()
            fn = record.filename_information()

            if not (record.is_active() or fn):
                continue

            first_cluster = -1
            cluster_list = []
            if record.is_directory():
                is_directory = True
            else:
                is_directory = False

            if record.is_active():
                is_deleted = False
            else:
                is_deleted = True

                data_attr = record.data_attribute()
                if data_attr and data_attr.non_resident() > 0:
                    cluster_list = self.runs_to_cluster_list(
                        data_attr.runlist().runs()
                    )
                    if cluster_list:
                        first_cluster = cluster_list[0][0]
                    else:
                        first_cluster = (
                            id_ * self.bytes_per_mft_record +
                            self.mft_abs_pos
                        ) // self.bytes_per_cluster

            si_create_time = datetime.datetime.utcfromtimestamp(0)
            si_modify_time = datetime.datetime.utcfromtimestamp(0)
            si_access_time = datetime.datetime.utcfromtimestamp(0)
            si_mft_time = datetime.datetime.utcfromtimestamp(0)
            if si:
                si_create_time = si.created_time()
                si_modify_time = si.modified_time()
                si_access_time = si.accessed_time()
                si_mft_time = si.changed_time()

            fn_create_time = datetime.datetime.utcfromtimestamp(0)
            fn_modify_time = datetime.datetime.utcfromtimestamp(0)
            fn_access_time = datetime.datetime.utcfromtimestamp(0)
            fn_mft_time = datetime.datetime.utcfromtimestamp(0)
            if fn:
                fn_create_time = fn.created_time()
                fn_modify_time = fn.modified_time()
                fn_access_time = fn.accessed_time()
                fn_mft_time = fn.changed_time()

            lsn = record.lsn()
            sn = record.sequence_number()

            yield (lsn, sn,
                   si_create_time, si_modify_time, si_access_time, si_mft_time,
                   fn_create_time, fn_modify_time, fn_access_time, fn_mft_time,
                   first_cluster, cluster_list,
                   '/%s' % record_path,
                   is_directory, is_deleted,
                   id_)


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

    def get_entries(self):
        entries = self.get_mft_records()

        return DataFrame(entries
                         if entries
                         else [(None,) * len(self.__mft_attr__)],
                         index=map(lambda x: x[-1], entries),
                         columns=self.__mft_attr__)
