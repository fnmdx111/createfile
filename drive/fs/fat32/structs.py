# encoding: utf-8
"""
    drive.fs.fat32.structs
    ~~~~~~~~~~~~~~~~~~~~~~

    This module implements certain structs used in constructing FAT32 objects.
"""
from decimal import Decimal
from functools import reduce
import os
from struct import unpack
from construct import *
from datetime import datetime
from pandas import DataFrame
from .. import Partition, EntryMixin
import pytz
from .speedup._op import find_cluster_lists
from drive.keys import *
from misc import STATE_LFN_ENTRY, STATE_DOS_ENTRY, MAGIC_END_SECTION, \
    clear_cur_obj, time_it, StateManager, STATE_START
from stream.auxiliary import BufferedClusterStream

FAT32BootSector = Struct(k_FAT32BootSector,
    Bytes       (k_jump_instruction, 3),
    String      (k_OEM_name, 8),
    ULInt16     (k_bytes_per_sector),
    ULInt8      (k_sectors_per_cluster),
    ULInt16     (k_number_of_reserved_sectors),
    ULInt8      (k_number_of_FATs),
    ULInt16(None),
    ULInt16(None),
    ULInt8      (k_media_descriptor),
    ULInt16(None),
    ULInt16     (k_sectors_per_track),
    ULInt16     (k_number_of_heads),
    ULInt32     (k_number_of_hidden_sectors),
    ULInt32     (k_number_of_sectors),
    ULInt32     (k_sectors_per_FAT),
    UBInt16     (k_drive_description), # 2 bytes for mirror flags, so use UBInt16
                                       # to keep its raw form
    ULInt16     (k_version),
    ULInt32     (k_cluster_number_of_root_directory_start),
    ULInt16     (k_sector_number_of_FS_info_sector),
    ULInt16     (k_sector_number_of_boot_sectors_backup),
    ULInt32(None),
    ULInt32(None),
    ULInt32(None),
    ULInt8      (k_drive_number),
    ULInt8(None),
    ULInt8      (k_extended_boot_signature),
    ULInt32     (k_volume_id),
    String      (k_volume_label, 11),
    String      (k_filesystem_type, 8),
    RepeatUntil(lambda obj, c: obj == MAGIC_END_SECTION,
                Field(k_ignored, 2)),
    Value(k_ignored, lambda _: MAGIC_END_SECTION),

    allow_overwrite=True
)

FAT32FSInformationSector = Struct(k_ignored,
    Magic(b'\x52\x52\x61\x41'),
    String(None, 0x1fa),
    Magic(MAGIC_END_SECTION),

    allow_overwrite=True
)

class FAT32DirectoryTableEntry(EntryMixin):
    """
    Represents the directory table entries (FDT).
    This class is a bit ugly due to the __slots__ mechanism, which, however, can
    improve the performance somehow.
    """
    __struct__ = Struct(k_FAT32DirectoryTableEntry,
                        String(k_short_file_name, 8),
                        String(k_short_extension, 3),
                        ULInt8(k_attribute),
                        ULInt8(None),
                        ULInt8(k_create_time_10ms),
                        ULInt16(k_create_time),
                        ULInt16(k_create_date),
                        ULInt16(k_access_date),
                        ULInt16(k_higher_cluster),
                        ULInt16(k_modify_time),
                        ULInt16(k_modify_date),
                        ULInt16(k_lower_cluster),
                        ULInt32(k_file_length))
    __slots__ = ['is_directory', 'cluster_list', 'avg_cluster',
                 'full_path', 'first_cluster',
                 'create_time',
                 'modify_time',
                 'access_date',
                 'skip', 'is_deleted',
                 'id']

    __attr__ = __slots__[:]
    __attr__.remove('skip')

    def __init__(self, raw, dir_name, state_mgr, current_obj, partition,
                 order_number):
        """
        :param raw: raw bytes read from stream.
        :param dir_name: parent path of the current entry.
        :param state_mgr: the state manager which holds the state of the name
                          state machine.
        :param current_obj: the content of the name state machine.
        :param partition: the partition on which this entry resides.
        """

        obj = self.__struct__.parse(raw)

        self.id = order_number

        self.skip = False
        self.is_deleted = obj[k_short_file_name].startswith(b'\xe5')

        self.is_directory = bool(obj[k_attribute] & 0x10)

        self.first_cluster = self._get_first_cluster(obj)
        self.cluster_list, self.avg_cluster =\
            partition.resolve_cluster_list(self.first_cluster)

        try:
            name, ext = self._get_names(obj, state_mgr, current_obj)
            if name == '.' or name == '..':
                self.skip = True
                return
        except UnicodeDecodeError:
            partition.logger.warning('%s unicode decode error, '
                                     'first cluster: %s, '
                                     'byte address: %s',
                                     dir_name, hex(self.first_cluster),
                                     hex(partition.abs_c2b(self.first_cluster)))
            name, ext = (str((obj[k_short_file_name]
                                 [1 if self.is_deleted else 0:]),
                             encoding='raw_unicode_escape'),
                         str(obj[k_short_extension]))

        self.full_path = os.path.join(dir_name, name)

        h, m, s = self._get_time(obj[k_create_time],
                                 obj[k_create_time_10ms])
        y, m_, d = self._get_date(obj[k_create_date])
        try:
            self.create_time = datetime(y, m_, d, h, m, int(s),
                                        int((Decimal(str(s)) - int(s))
                                            * 1000000),
                                        tzinfo=pytz.utc)
            # TODO implement customizable timezone
        except ValueError:
            partition.logger.warning('%s\\%s: invalid date %s, %s, %s',
                                     dir_name, name, y, m_, d)
            self.skip = True
            return

        h, m, s = self._get_time(obj[k_modify_time], 0)
        y, m_, d = self._get_date(obj[k_modify_date])
        try:
            self.modify_time = datetime(y, m_, d, h, m, int(s),
                                        tzinfo=pytz.utc)
            # TODO implement customizable timezone
        except ValueError:
            partition.logger.warning('%s\\%s: invalid date %s, %s, %s',
                                     dir_name, name, y, m_, d)
            self.skip = True
            return

        y, m_, d = self._get_date(obj[k_access_date])
        try:
            self.access_date = datetime(y, m_, d, 0, 0, 0,
                                        tzinfo=pytz.utc)
        except ValueError:
            partition.logger.warning('%s\\%s: invalid date %s, %s, %s',
                                     dir_name, name, y, m_, d)
            self.skip = True
            return

    def _get_names(self, obj, state_mgr, current_obj):
        """Get the file name of this entry.

        :param obj: the context object.
        :param state_mgr: the state manager.
        :param current_obj: the content of the name state machine.
        """

        ext = ''
        if state_mgr.is_(STATE_LFN_ENTRY):
            name = current_obj['name']
            if self.is_deleted:
                name = '(deleted) ' + name
            if not self.is_directory:
                ext = name.rsplit('.')[-1] if '.' in name else ''

            state_mgr.transit_to(STATE_DOS_ENTRY)
            current_obj['name'] = ''

        else:
            name = obj[k_short_file_name].strip()
            if self.is_deleted:
                # TODO add a function which tries both gbk and unicode to decode
                # TODO the file names
                name = '(deleted) ' + str(name[1:], encoding='gbk')
            else:
                name = str(name, encoding='gbk')

            if not self.is_directory:
                ext = str(obj[k_short_extension].strip(), encoding='gbk')
                name = '.'.join((name, ext)).strip('.')
            name = name.lower()
            ext = ext.lower()

        return name, ext

    @staticmethod
    def _get_checksum(obj):
        """Calculate the checksum of this entry.

        :param obj: the context object.
        """
        # TODO checksum checking is not yet implemented
        return reduce(lambda sum_, c: (0x80 if sum_ & 1 else 0 +
                                       (sum_ >> 1) +
                                       c) & 0xff,
                      b''.join((obj[k_short_file_name],
                                 obj[k_short_extension])),
                      0)

    @staticmethod
    def _get_time(word, byte):
        """Get the timestamp of this entry.

        :param word, byte: the two arguments in which timestamp is stored.
        """

        return ((word & 0xf800) >> 11,
                (word & 0x07e0) >> 5,
                (word & 0x001f) * 2 + byte * .01)

    @staticmethod
    def _get_date(word):
        """Get the date of this entry.

        :param word: the word in which date is stored.
        """

        return (((word & 0xfe00) >> 9) + 1980,
                (word & 0x01e0) >> 5,
                word & 0x001f)

    @staticmethod
    def _get_first_cluster(obj):
        """Get first cluster of the file represented by this entry.

        :param obj: the context object.
        """

        return obj[k_higher_cluster] << 16 | obj[k_lower_cluster]


class FAT32LongFilenameEntry:
    """
    Class represents long filename entry (LFN).
    """
    __struct__ = Struct(k_FAT32LongFilenameEntry,
                        ULInt8(k_sequence_number),
                        String(k_name_1, 10),
                        ULInt8(None),
                        ULInt8(k_type),
                        ULInt8(k_checksum),
                        String(k_name_2, 12),
                        ULInt16(None),
                        String(k_name_3, 4))

    __slots__ = ['abort', 'is_deleted']

    def __init__(self, raw, state_mgr, current_obj, partition):
        """Same as the parameters in :class:`FAT32DirectoryTableEntry`. Pass."""

        obj = self.__struct__.parse(raw)

        self.abort = False
        self.is_deleted = False

        seq_number = obj[k_sequence_number]
        if seq_number == 0xe5:
            # deleted entry
            self.is_deleted = True
            state_mgr.transit_to(STATE_LFN_ENTRY)
        elif seq_number & 0x40:
            # first (logically last) LFN entry
            if state_mgr.is_(STATE_LFN_ENTRY):
                partition.logger.warning('detected overwritten LFN')
                clear_cur_obj(current_obj)

            state_mgr.transit_to(STATE_LFN_ENTRY)
            current_obj['checksum'] = obj[k_checksum]
        else:
            # assert state_mgr.is_(STATE_LFN_ENTRY)
            if not state_mgr.is_(STATE_LFN_ENTRY):
                partition.logger.warning('invalid LFN non-starting entry')

            if current_obj['checksum'] != obj[k_checksum]:
                # it's only possible that the checksum of the first entry and the
                # checksum of current_obj are not the same, the following entry
                # has to have the same checksum with the current_obj, there must
                # be something wrong here in this situation, so we choose to
                # abort immediately and consider this subdirectory corrupted
                self.abort = True
                return

            seq_number &= 0x1f
            if seq_number == 1:
                # LFN ends
                pass

        current_obj['name'] = self._get_entry_name(obj) + current_obj['name']

    @staticmethod
    def _get_entry_name(obj):
        """Get the name represented by this entry.

        :param obj: the context object."""

        try:
            return str(b''.join((obj[k_name_1],
                                 obj[k_name_2],
                                 obj[k_name_3])),
                       encoding='utf-16').split('\x00')[0]
        except UnicodeDecodeError:
            print('Unicode decode error in _get_entry_name')
            return 'unicode decode error'


class FAT32(Partition):
    """
    Class represents FAT32 partitions.
    """
    type = 'FAT32'

    _ul_int32 = ULInt32(None)

    def __init__(self, stream, preceding_bytes,
                 read_fat2=False, ui_handler=None):
        """
        :param stream: stream to parse against.
        :param preceding_bytes: absolute position of this partition.
        :param read_fat2: if false, the second FAT won't be read.
        """

        super(FAT32, self).__init__(FAT32.type, stream, preceding_bytes,
                                    lambda s: FAT32BootSector.parse_stream(s),
                                    ui_handler=ui_handler)

        self.bytes_per_sector = self.boot_sector[k_bytes_per_sector]
        self.bytes_per_cluster = self.bytes_per_sector *\
                                 self.boot_sector[k_sectors_per_cluster]
        self.logger.info('read boot sector, bytes per sector is %d, '
                         'bytes per cluster is %d',
                         self.bytes_per_sector, self.bytes_per_cluster)
        # assert self.bytes_per_sector == 512

        self.bytes_per_fat = self.s2b(self.boot_sector[k_sectors_per_FAT])

        self.logger.info('reading fs info sector')
        FAT32FSInformationSector.parse_stream(stream)

        self.read_fat2 = read_fat2

        self.fat1, self.number_of_eoc_1, self.fat2, self.number_of_eoc_2 = (
            {}, 0, {}, 0
        )

        self.fat_abs_pos = self.s2b(
            self.boot_sector[k_number_of_reserved_sectors]
        )
        self.fat_abs_pos += preceding_bytes

        self.data_section_offset = self.fat_abs_pos + 2 * self.bytes_per_fat

        self.fdt = {}

        self.items_count = 0

    def read_fdt(self):
        """Read the FDT entries."""

        self.logger.info('reading FDT')
        self.fdt = self.get_fdt()

    def _jump(self, size):
        """Relatively jump to another location in stream.

        :param size: the length of the leap.
        """

        self.stream.seek(size, os.SEEK_CUR)

    def s2b(self, n):
        """Calculate sector to byte.

        :param n: the number of the sector.
        """

        return self.bytes_per_sector * n

    def c2b(self, n):
        """Calculate cluster to byte.

        :param n: the number of the cluster.
        """

        return self.bytes_per_cluster * n

    def _next_ul_int32(self):
        """Read the next 4 bytes as an 32-bit unsigned integer."""

        return unpack('<I', self.stream.read(4))[0]

    _eoc_magic = 0x0ffffff8
    def _is_eoc(self, n):
        """Determine if it reaches the end of cluster (EOC).

        :param n: the ULInt32 to be tested against.
        """

        return n & self._eoc_magic == self._eoc_magic

    @time_it
    def get_fat(self):
        """Get file allocation table from current stream position,
        returns the table represented in dict and number of EOCs."""
        _0 = self._next_ul_int32()
        _1 = self._next_ul_int32()
        assert _0 & self._eoc_magic == self._eoc_magic
        # assert _1 == 0xffffffff or _1 == 0xfffffff
        # due to some un-standard implementations

        number_of_fat_items = self.bytes_per_fat // 4

        cluster_head = {}
        obj = {}

        find_cluster_lists(self, cluster_head, obj, number_of_fat_items)

        return obj, 0

    def get_fdt(self, root_dir_name='/'):
        """Read the FDT entries in order.

        :param root_dir_name: optional, name of the root directory.
        """

        # task := (directory_name, fdt_abs_start_byte_pos)
        __tasks__ = [(root_dir_name,
                      self.resolve_cluster_list(2)[0])]

        entries, create_time_indices = [], []

        while __tasks__:
            dir_name, cluster_list = __tasks__.pop(0)

            if dir_name.startswith(u'\u00e5'):
                continue

            _e, _ct = self._discover(__tasks__, dir_name, cluster_list)

            entries.extend(_e)
            create_time_indices.extend(_ct)

        self.logger.info('found %s files and dirs in total', len(entries))

        return DataFrame(entries if entries else
                         [(None,) * len(FAT32DirectoryTableEntry.__attr__)],
                         index=map(lambda x: x[-1], entries),
                         columns=FAT32DirectoryTableEntry.__attr__)

    def resolve_cluster_list(self, first_cluster, fat=None):
        """Resolve the cluster lists by first_cluster.

        :param first_cluster: first cluster number.
        :param fat: optional, the FAT used to be resolved against. If not set,
                    the first FAT is used.
        """

        fat = fat or self.fat1

        if first_cluster in fat:
            cl = fat[first_cluster]
            total_sum = sum((e - s + 1) * (e + s) / 2 for s, e in cl)
            total_n = sum(e - s + 1 for s, e, in cl)

            return cl, total_sum / total_n
        else:
            return (), 0

    def abs_c2b(self, cluster):
        """Cluster to absolute position in stream.

        :param cluster: cluster which is to be converted.
        """

        return self.c2b(cluster - 2) + self.data_section_offset

    def _discover(self, tasks, dir_name, cluster_list):
        """Discover subdirectories.

        :param tasks: a stack which stores the following discovery tasks.
        :param dir_name: the name of the current directory, i.e. parent
                         directory.
        :param cluster_list: the cluster list of this task.
        """

        if 'System Volume Information' in dir_name:
            return [], []

        __blank__ = b'\x00'

        __state__ = StateManager(STATE_START)
        __cur_obj__ = {'name': '', 'checksum': 0}

        entries, create_time_indices = [], []

        with BufferedClusterStream(self.stream,
                                   cluster_list,
                                   self.abs_c2b,
                                   self.bytes_per_cluster) as stream:
            while True:
                try:
                    raw = stream.read(32)
                except StopIteration:
                    # we just ran out of clusters, simply do a break here
                    break

                if len(raw) < 32:
                    continue
                elif raw.startswith(__blank__):
                    continue

                attribute = raw[0xb]
                if attribute == 0xf:
                    entry = FAT32LongFilenameEntry(raw,
                                                   __state__,
                                                   __cur_obj__,
                                                   self)
                    if entry.abort:
                        break
                else:
                    entry = FAT32DirectoryTableEntry(raw, dir_name,
                                                     __state__,
                                                     __cur_obj__,
                                                     self,
                                                     self.items_count)
                    self.items_count += 1
                    if attribute == 0xb:
                        print('label: %s' % entry.full_path[1:])

                    if entry.skip:
                        continue

                    entries.append(entry.to_tuple())
                    create_time_indices.append(entry.create_time)

                    if entry.is_directory:
                        if entry.is_deleted:
                            continue
                        # append new directory task to tasks
                        if entry.first_cluster in self.fat1:
                            tasks.append((entry.full_path,
                                          self.fat1[entry.first_cluster]))
                        else:
                            self.logger.warning('found deleted directory at'
                                                ' %s' % entry.first_cluster)

        return entries, create_time_indices

    def read_fats(self):
        self.stream.seek(self.fat_abs_pos, os.SEEK_SET)
        self.logger.info('stream jumped to %d and ready to read FAT',
                         self.fat_abs_pos)

        self.logger.info('reading FAT')
        res1 = self.fat1, self.number_of_eoc_1 = self.get_fat()
        self.logger.info('read FAT, size of FAT is %d, number of EOCs is %d',
                         self.bytes_per_fat, self.number_of_eoc_1)
        if not self.read_fat2:
            self._jump(self.bytes_per_fat)
            self.fat2, self.number_of_eoc_2 = res1
        else:
            self.fat2, self.number_of_eoc_2 = self.get_fat()

    def get_entries(self):
        self.items_count = 0

        self.read_fats()

        return self.get_fdt()
