# encoding: utf-8
from collections import defaultdict
import os
from struct import unpack
from construct import Struct, ULInt32, ULInt8, ULInt16, ULInt64, Bytes
from .misc import Unused, _local_timestamp
from drive.keys import *


class AttributeHeader:

    _common_header = Struct(k_common_header,
        # ULInt32(k_attribute_type),
        ULInt32(k_size_of_attribute),
        ULInt8(k_is_resident),
        ULInt8(k_length_of_name),
        ULInt16(k_offset_to_name),
        ULInt16(k_flags),
        ULInt16(k_attribute_id),
    )

    _resident_header = Struct(k_resident_header,
        ULInt32(k_size_of_attribute_content),
        ULInt16(k_offset_to_attribute_content),
        ULInt8(k_is_indexed),
        Unused(1)
    )

    _non_resident_header = Struct(k_non_resident_header,
        ULInt64(k_starting_vcn_of_data_runs),
        ULInt64(k_ending_vcn_of_data_runs),
        ULInt16(k_offset_to_data_runs),
        ULInt16(k_compression_unit),
        Unused(4),
        ULInt64(k_allocated_size),
        ULInt64(k_logical_size),
        ULInt64(k_initial_size)
    )

    def __init__(self, stream):
        self.is_end_of_attributes = False

        self._stream = stream
        self.name = ''

        self.size, self._abs_pos = 0, 0
        with self:
            self.type = unpack('<I', stream.read(4))[0]
            if self.type == 0xffffffff:
                self.is_end_of_attributes = True
                return

            self._common_header = self._common_header.parse_stream(stream)

            self.is_resident = not self._common_header[k_is_resident]
            if self.is_resident:
                self._rest_header = self._resident_header.parse_stream(stream)
                self.data_runs = ()
            else:
                self._rest_header =\
                    self._non_resident_header.parse_stream(stream)
                self.data_runs = self._read_data_runs()

            self._read_name()

    def __enter__(self):
        self._abs_pos = self._stream.tell()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.size = self._stream.tell() - self._abs_pos

    def __getitem__(self, item):
        if item in self._common_header:
            return self._common_header[item]
        else:
            return self._rest_header[item]

    @staticmethod
    def _pad_to_uint64(chars):
        return chars + b'\x00' * (8 - len(chars))

    def _read_data_runs(self):
        self._stream.seek(self._abs_pos +
                          self._rest_header[k_offset_to_data_runs],
                          os.SEEK_SET)
        ret = []
        while True:
            sizes = unpack('B', self._stream.read(1))[0]
            if not sizes:
                return ret
            _size_of_starting_vcn = sizes >> 4
            _size_of_length = sizes & 0xf

            length = unpack('<Q', self._pad_to_uint64(
                self._stream.read(_size_of_length)))[0]
            # length may overflow if _size_of_length > 8, which can be up to 0xf

            starting_vcn = unpack('<q', self._pad_to_uint64(
                self._stream.read(_size_of_starting_vcn)))[0]
            # starting_vcn is unlikely to overflow, because the maximum size of
            # clusters seems to be 8

            ret.append([starting_vcn, length])

    def _read_name(self):
        size_of_name = self._common_header[k_length_of_name] * 2
        if self._common_header[k_length_of_name]:
            self._stream.seek(self._abs_pos +
                              self._common_header[k_offset_to_name],
                              os.SEEK_SET)
            self.name = str(self._stream.read(size_of_name),
                            encoding='utf-16')


class Attribute:

    __registry__ = {}

    def __init__(self, attribute_header, stream):
        self.attribute_header = attribute_header
        self.stream = stream

        self.abs_pos = 0

        self.name = attribute_header.name
        self.is_resident = attribute_header.is_resident

    def __enter__(self):
        self.abs_pos = self.stream.tell() - self.attribute_header.size

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._finish()

    def _finish(self):
        self.stream.seek(self.abs_pos, os.SEEK_SET)
        self.stream.seek(self.attribute_header[k_size_of_attribute],
                         os.SEEK_CUR)
        del self.stream


def _make_registry():
    class UnusedAttribute(Attribute):
        type = 0xff
        def __init__(self, _1, _2):
            super(UnusedAttribute, self).__init__(_1, _2)
            with self:
                pass

    __registry__ = defaultdict(lambda: UnusedAttribute)
    def _(cls):
        __registry__[cls.type] = cls
        return cls

    return __registry__, _

attribute_registry, register = _make_registry()


@register
class StandardInformation(Attribute):

    type = 0x10
    __struct__ = Struct(None,
        ULInt64(k_create_time),
        ULInt64(k_modify_time),
        ULInt64(k_MFT_change_time),
        ULInt64(k_access_time),
        ULInt32(k_flags),
        ULInt32(k_maximum_version_number),
        ULInt32(k_version_number),
        Unused(4 + 4 + 4 + 8 + 8), # class id, owner id, security id, quota
                                   # charged and update sequence number are
                                   # skipped
    )

    def __init__(self, attribute_header, stream):
        super(StandardInformation, self).__init__(attribute_header, stream)

        with self:
            self.body = self.__struct__.parse_stream(stream)

            self.create_time = _local_timestamp(self.body[k_create_time])
            self.modify_time = _local_timestamp(self.body[k_modify_time])
            self.access_time = _local_timestamp(self.body[k_access_time])
            self.mft_change_time = _local_timestamp(self.body[k_MFT_change_time])


@register
class FileName(Attribute):

    type = 0x30
    __struct__ = Struct(None,
        ULInt64(k_parent_reference),
        ULInt64(k_create_time),
        ULInt64(k_modify_time),
        ULInt64(k_MFT_change_time),
        ULInt64(k_access_time),
        ULInt64(k_logical_size),
        ULInt64(k_allocated_size),
        ULInt32(k_flags),
        Unused(4),
        ULInt8(k_length_of_name),
        ULInt8(k_filename_namespace)
    )

    def __init__(self, attribute_header, stream):
        super(FileName, self).__init__(attribute_header, stream)

        with self:
            self.body = self.__struct__.parse_stream(stream)

            self.create_time = _local_timestamp(self.body[k_create_time])
            self.modify_time = _local_timestamp(self.body[k_modify_time])
            self.access_time = _local_timestamp(self.body[k_access_time])
            self.mft_change_time = _local_timestamp(self.body[k_MFT_change_time])

            self.filename = str(stream.read(self.body[k_length_of_name] * 2),
                                encoding='utf-16')


@register
class ObjectID(Attribute):

    type = 0x40
    __struct__ = Struct(None,
        Bytes(k_GUID_object_id, 16),
        Bytes(k_GUID_birth_volume_id, 16),
        Bytes(k_GUID_birth_object_id, 16),
        Bytes(k_GUID_domain_id, 16)
    )

    def __init__(self, attribute_header, stream):
        super(ObjectID, self).__init__(attribute_header, stream)

        with self:
            self.body = self.__struct__.parse_stream(stream)


@register
class VolumeName(Attribute):

    type = 0x60

    def __init__(self, attribute_header, stream):
        super(VolumeName, self).__init__(attribute_header, stream)

        with self:
            length_of_name = (self.attribute_header.size - 16) * 2
            self.volume_name = str(stream.read(length_of_name),
                                   encoding='utf-16')


@register
class Data(Attribute):

    type = 0x80

    def __init__(self, attribute_header, stream):
        super(Data, self).__init__(attribute_header, stream)

        with self:
            self.data_runs = self.attribute_header.data_runs


def attributes(stream):
    while True:
        header = AttributeHeader(stream)
        if header.is_end_of_attributes:
            return
        yield attribute_registry[header.type](header, stream)
