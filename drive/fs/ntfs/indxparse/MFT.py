#    This file is part of INDXParse.
#
#   Copyright 2011 Will Ballenthin <william.ballenthin@mandiant.com>
#                    while at Mandiant <http://www.mandiant.com>
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
#   Version v.1.1.8
import array
import os
import struct
import logging
from datetime import datetime

from .BinaryParser import Block
from .BinaryParser import Nestable
from .BinaryParser import align
from .BinaryParser import ParseException
from .BinaryParser import OverrunBufferException
from .BinaryParser import read_byte
from .BinaryParser import read_word
from .BinaryParser import read_dword
from .misc import Cache
from stream.auxiliary.mft_stream import MFTExhausted


class INDXException(Exception):
    """
    Base Exception class for INDX parsing.
    """
    def __init__(self, value):
        """
        Constructor.
        Arguments:
        - `value`: A string description.
        """
        super(INDXException, self).__init__()
        self._value = value

    def __str__(self):
        return "INDX Exception: %s" % (self._value)


class FixupBlock(Block):

    sector_size = 512

    @classmethod
    def set_sector_size(cls, sector_size):
        cls.sector_size = sector_size

    def __init__(self, buf, offset, parent):
        super(FixupBlock, self).__init__(buf, offset)

    def fixup(self, num_fixups, fixup_value_offset):
        fixup_value = self.unpack_word(fixup_value_offset)

        for i in range(0, num_fixups - 1):
            fixup_offset = self.sector_size * (i + 1) - 2
            check_value = self.unpack_word(fixup_offset)

            if check_value != fixup_value:
                logging.warning("Bad fixup at %s", hex(self.offset() + fixup_offset))
                continue

            new_value = self.unpack_word(fixup_value_offset + 2 + 2 * i)
            self.pack_word(fixup_offset, new_value)

            check_value = self.unpack_word(fixup_offset)
            logging.debug("Fixup verified at %s and patched from %s to %s.",
                          hex(self.offset() + fixup_offset),
                          hex(fixup_value), hex(check_value))


class INDEX_ENTRY_FLAGS:
    """
    sizeof() == WORD
    """
    INDEX_ENTRY_NODE = 0x1
    INDEX_ENTRY_END = 0x2
    INDEX_ENTRY_SPACE_FILLER = 0xFFFF


class INDEX_ENTRY_HEADER(Block, Nestable):
    def __init__(self, buf, offset, parent):
        super(INDEX_ENTRY_HEADER, self).__init__(buf, offset)
        self.declare_field("word", "length", 0x8)
        self.declare_field("word", "key_length")
        self.declare_field("word", "index_entry_flags")  # see INDEX_ENTRY_FLAGS
        self.declare_field("word", "reserved")

    @staticmethod
    def structure_size(buf, offset, parent):
        return 0x10

    def __len__(self):
        return 0x10

    def is_index_entry_node(self):
        return self.index_entry_flags() & INDEX_ENTRY_FLAGS.INDEX_ENTRY_NODE

    def is_index_entry_end(self):
        return self.index_entry_flags() & INDEX_ENTRY_FLAGS.INDEX_ENTRY_END

    def is_index_entry_space_filler(self):
        return self.index_entry_flags() & INDEX_ENTRY_FLAGS.INDEX_ENTRY_SPACE_FILLER


class MFT_INDEX_ENTRY_HEADER(INDEX_ENTRY_HEADER):
    """
    Index used by the MFT for INDX attributes.
    """
    def __init__(self, buf, offset, parent):
        super(MFT_INDEX_ENTRY_HEADER, self).__init__(buf, offset, parent)
        self.declare_field("qword", "mft_reference", 0x0)


class SECURE_INDEX_ENTRY_HEADER(INDEX_ENTRY_HEADER):
    """
    Index used by the $SECURE file indices SII and SDH
    """
    def __init__(self, buf, offset, parent):
        super(SECURE_INDEX_ENTRY_HEADER, self).__init__(buf, offset, parent)
        self.declare_field("word", "data_offset", 0x0)
        self.declare_field("word", "data_length")
        self.declare_field("dword", "reserved")


class INDEX_ENTRY(Block,  Nestable):
    """
    NOTE: example structure. See the more specific classes below.
      Probably do not instantiate.
    """
    def __init__(self, buf, offset, parent):
        super(INDEX_ENTRY, self).__init__(buf, offset)
        self.declare_field(INDEX_ENTRY_HEADER, "header", 0x0)
        self.add_explicit_field(0x10, "string", "data")

    def data(self):
        start = self.offset() + 0x10
        end = start + self.header().key_length()
        return self._buf[start:end]

    @staticmethod
    def structure_size(buf, offset, parent):
        return read_word(buf, offset + 0x8)

    def __len__(self):
        return self.header().length()

    def is_valid(self):
        return True


class MFT_INDEX_ENTRY(Block, Nestable):
    """
    Index entry for the MFT directory index $I30, attribute type 0x90.
    """
    def __init__(self, buf, offset, parent):
        super(MFT_INDEX_ENTRY, self).__init__(buf, offset)
        self.declare_field(MFT_INDEX_ENTRY_HEADER, "header", 0x0)
        self.declare_field(FilenameAttribute, "filename_information")

    @staticmethod
    def structure_size(buf, offset, parent):
        return read_word(buf, offset + 0x8)

    def __len__(self):
        return self.header().length()

    def is_valid(self):
        # this is a bit of a mess, but it should work
        recent_date = datetime(1990, 1, 1, 0, 0, 0)
        future_date = datetime(2025, 1, 1, 0, 0, 0)
        try:
            fn = self.filename_information()
        except:
            return False
        if not fn:
            return False
        try:
            return fn.modified_time() > recent_date and \
                   fn.accessed_time() > recent_date and \
                   fn.changed_time() > recent_date and \
                   fn.created_time() > recent_date and \
                   fn.modified_time() < future_date and \
                   fn.accessed_time() < future_date and \
                   fn.changed_time() < future_date and \
                   fn.created_time() < future_date
        except ValueError:
            return False


class SII_INDEX_ENTRY(Block, Nestable):
    """
    Index entry for the $SECURE:$SII index.
    """
    def __init__(self, buf, offset, parent):
        super(SII_INDEX_ENTRY, self).__init__(buf, offset)
        self.declare_field(SECURE_INDEX_ENTRY_HEADER, "header", 0x0)
        self.declare_field("dword", "security_id")

    @staticmethod
    def structure_size(buf, offset, parent):
        return read_word(buf, offset + 0x8)

    def __len__(self):
        return self.header().length()

    def is_valid(self):
        # TODO(wb): test
        return 1 < self.header().length() < 0x30 and \
            1 < self.header().key_lenght() < 0x20


class SDH_INDEX_ENTRY(Block, Nestable):
    """
    Index entry for the $SECURE:$SDH index.
    """
    def __init__(self, buf, offset, parent):
        super(SDH_INDEX_ENTRY, self).__init__(buf, offset)
        self.declare_field(SECURE_INDEX_ENTRY_HEADER, "header", 0x0)
        self.declare_field("dword", "hash")
        self.declare_field("dword", "security_id")

    @staticmethod
    def structure_size(buf, offset, parent):
        return read_word(buf, offset + 0x8)

    def __len__(self):
        return self.header().length()

    def is_valid(self):
        # TODO(wb): test
        return 1 < self.header().length() < 0x30 and \
            1 < self.header().key_lenght() < 0x20


class INDEX_HEADER_FLAGS:
    SMALL_INDEX = 0x0  # MFT: INDX_ROOT only
    LARGE_INDEX = 0x1  # MFT: requires INDX_ALLOCATION
    LEAF_NODE = 0x1
    INDEX_NODE = 0x2
    NODE_MASK = 0x1


class INDEX_HEADER(Block, Nestable):
    def __init__(self, buf, offset, parent):
        super(INDEX_HEADER, self).__init__(buf, offset)
        self.declare_field("dword", "entries_offset", 0x0)
        self.declare_field("dword", "index_length")
        self.declare_field("dword", "allocated_size")
        self.declare_field("byte", "index_header_flags")  # see INDEX_HEADER_FLAGS
        # then 3 bytes padding/reserved

    @staticmethod
    def structure_size(buf, offset, parent):
        return 0x1C

    def __len__(self):
        return 0x1C

    def is_small_index(self):
        return self.index_header_flags() & INDEX_HEADER_FLAGS.SMALL_INDEX

    def is_large_index(self):
        return self.index_header_flags() & INDEX_HEADER_FLAGS.LARGE_INDEX

    def is_leaf_node(self):
        return self.index_header_flags() & INDEX_HEADER_FLAGS.LEAF_NODE

    def is_index_node(self):
        return self.index_header_flags() & INDEX_HEADER_FLAGS.INDEX_NODE

    def is_NODE_MASK(self):
        return self.index_header_flags() & INDEX_HEADER_FLAGS.NODE_MASK


class INDEX(Block, Nestable):
    def __init__(self, buf, offset, parent, index_entry_class):
        self._INDEX_ENTRY = index_entry_class
        super(INDEX, self).__init__(buf, offset)
        self.declare_field(INDEX_HEADER, "header", 0x0)
        self.add_explicit_field(self.header().entries_offset(),
                                INDEX_ENTRY, "entries")
        slack_start = self.header().entries_offset() + self.header().index_length()
        self.add_explicit_field(slack_start, INDEX_ENTRY, "slack_entries")

    @staticmethod
    def structure_size(buf, offset, parent):
        return read_dword(buf, offset + 0x8)

    def __len__(self):
        return self.header().allocated_size()

    def entries(self):
        """
        A generator that returns each INDEX_ENTRY associated with this node.
        """
        offset = self.header().entries_offset()
        if offset == 0:
            logging.debug("No entries in this allocation block.")
            return
        while offset <= self.header().index_length() - 0x52:
            logging.debug("Entry has another entry after it.")
            e = self._INDEX_ENTRY(self._buf, self.offset() + offset, self)
            offset += e.length()
            yield e
        logging.debug("No more entries.")

    def slack_entries(self):
        """
        A generator that yields INDEX_ENTRYs found in the slack space
        associated with this header.
        """
        offset = self.header().index_length()
        try:
            while offset <= self.header().allocated_size - 0x52:
                try:
                    logging.debug("Trying to find slack entry at %s.", hex(offset))
                    e = self._INDEX_ENTRY(self._buf, offset, self)
                    if e.is_valid():
                        logging.debug("Slack entry is valid.")
                        offset += e.length() or 1
                        yield e
                    else:
                        logging.debug("Slack entry is invalid.")
                        raise ParseException("Not a deleted entry")
                except ParseException:
                    logging.debug("Scanning one byte forward.")
                    offset += 1
        except struct.error:
            logging.debug("Slack entry parsing overran buffer.")
            pass


def INDEX_ROOT(Block, Nestable):
    def __init__(self, buf, offset, parent):
        super(INDEX_ROOT, self).__init__(buf, offset)
        self.declare_field("dword", "type", 0x0)
        self.declare_field("dword", "collation_rule")
        self.declare_field("dword", "index_record_size_bytes")
        self.declare_field("byte",  "index_record_size_clusters")
        self.declare_field("byte", "unused1")
        self.declare_field("byte", "unused2")
        self.declare_field("byte", "unused3")
        self._index_offset = self.current_field_offset()
        self.add_explicit_field(self._index_offset, INDEX, "index")

    def index(self):
        return INDEX(self._buf, self.offset(self._index_offset),
                     self, MFT_INDEX_ENTRY)

    @staticmethod
    def structure_size(buf, offset, parent):
        return 0x10 + INDEX.structure_size(buf, offset + 0x10, parent)

    def __len__(self):
        return 0x10 + len(self.index())


class NTATTR_STANDARD_INDEX_HEADER(Block):
    def __init__(self, buf, offset, parent):
        logging.debug("INDEX NODE HEADER at %s.", hex(offset))
        super(NTATTR_STANDARD_INDEX_HEADER, self).__init__(buf, offset)
        self.declare_field("dword", "entry_list_start", 0x0)
        self.declare_field("dword", "entry_list_end")
        self.declare_field("dword", "entry_list_allocation_end")
        self.declare_field("dword", "flags")
        self.declare_field("binary", "list_buffer", \
                           self.entry_list_start(),
                           self.entry_list_allocation_end() - self.entry_list_start())

    def entries(self):
        """
        A generator that returns each INDX entry associated with this node.
        """
        offset = self.entry_list_start()
        if offset == 0:
            return

        # 0x52 is an approximate size of a small index entry
        while offset <= self.entry_list_end() - 0x52:
            e = IndexEntry(self._buf, self.offset() + offset, self)
            offset += e.length()
            yield e

    def slack_entries(self):
        """
        A generator that yields INDX entries found in the slack space
        associated with this header.
        """
        offset = self.entry_list_end()
        try:
            # 0x52 is an approximate size of a small index entry
            while offset <= self.entry_list_allocation_end() - 0x52:
                try:
                    e = SlackIndexEntry(self._buf, offset, self)
                    if e.is_valid():
                        offset += e.length() or 1
                        yield e
                    else:
                        raise ParseException("Not a deleted entry")
                except ParseException:
                    # ensure we're always moving forward
                    offset += 1
        except struct.error:
            pass


class IndexRootHeader(Block):
    def __init__(self, buf, offset, parent):
        logging.debug("INDEX ROOT HEADER at %s.", hex(offset))
        super(IndexRootHeader, self).__init__(buf, offset)
        self.declare_field("dword", "type", 0x0)
        self.declare_field("dword", "collation_rule")
        self.declare_field("dword", "index_record_size_bytes")
        self.declare_field("byte",  "index_record_size_clusters")
        self.declare_field("byte", "unused1")
        self.declare_field("byte", "unused2")
        self.declare_field("byte", "unused3")
        self._node_header_offset = self.current_field_offset()

    def node_header(self):
        return NTATTR_STANDARD_INDEX_HEADER(self._buf,
                               self.offset() + self._node_header_offset,
                               self)


class IndexRecordHeader(FixupBlock):
    def __init__(self, buf, offset, parent):
        logging.debug("INDEX RECORD HEADER at %s.",  hex(offset))
        super(IndexRecordHeader, self).__init__(buf, offset, parent)
        self.declare_field("dword", "magic", 0x0)
        self.declare_field("word",  "usa_offset")
        self.declare_field("word",  "usa_count")
        self.declare_field("qword", "lsn")
        self.declare_field("qword", "vcn")
        self._node_header_offset = self.current_field_offset()
        self.fixup(self.usa_count(), self.usa_offset())

    def node_header(self):
        return NTATTR_STANDARD_INDEX_HEADER(self._buf,
                               self.offset() + self._node_header_offset,
                               self)


class INDEX_ALLOCATION(FixupBlock):
    def __init__(self, buf, offset, parent):
        """

        TODO(wb): figure out what we're doing with the fixups!

        """
        super(INDEX_ALLOCATION, self).__init__(buf, offset, parent)
        self.declare_field("dword", "magic", 0x0)
        self.declare_field("word",  "usa_offset")
        self.declare_field("word",  "usa_count")
        self.declare_field("qword", "lsn")
        self.declare_field("qword", "vcn")
        self._index_offset = self.current_field_offset()
        self.add_explicit_field(self._index_offset, INDEX, "index")
        # TODO(wb): we do not want to modify data here.
        #   best to make a copy and use that.
        #   Until then, this is not a nestable structure.
        self.fixup(self.usa_count(), self.usa_offset())

    def index(self):
        return INDEX(self._buf, self.offset(self._index_offset),
                     self, MFT_INDEX_ENTRY)

    @staticmethod
    def structure_size(buf, offset, parent):
        return 0x30 + INDEX.structure_size(buf, offset + 0x10, parent)

    def __len__(self):
        return 0x30 + len(self.index())



class IndexEntry(Block):
    def __init__(self, buf, offset, parent):
        logging.debug("INDEX ENTRY at %s.", hex(offset))
        super(IndexEntry, self).__init__(buf, offset)
        self.declare_field("qword", "mft_reference", 0x0)
        self.declare_field("word", "length")
        self.declare_field("word", "filename_information_length")
        self.declare_field("dword", "flags")
        self.declare_field("binary", "filename_information_buffer", \
                           self.current_field_offset(),
                           self.filename_information_length())
        self.declare_field("qword", "child_vcn",
                           align(self.current_field_offset(), 0x8))

    def filename_information(self):
        return FilenameAttribute(self._buf,
                                 self.offset() + self._off_filename_information_buffer,
                                 self)


class StandardInformationFieldDoesNotExist(Exception):
    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return "Standard Information attribute field does not exist: %s" % (self._msg)


class StandardInformation(Block):
    # TODO(wb): implement sizing so we can make this nestable
    def __init__(self, buf, offset, parent):
        logging.debug("STANDARD INFORMATION ATTRIBUTE at %s.", hex(offset))
        super(StandardInformation, self).__init__(buf, offset)
        self.declare_field("filetime", "created_time", 0x0)
        self.declare_field("filetime", "modified_time")
        self.declare_field("filetime", "changed_time")
        self.declare_field("filetime", "accessed_time")
        self.declare_field("dword", "attributes")
        self.declare_field("binary", "reserved", self.current_field_offset(), 0xC)
        # self.declare_field("dword", "owner_id", 0x30)  # Win2k+, NTFS 3.x
        # self.declare_field("dword", "security_id")  # Win2k+, NTFS 3.x
        # self.declare_field("qword", "quota_charged")  # Win2k+, NTFS 3.x
        # self.declare_field("qword", "usn")  # Win2k+, NTFS 3.x

    # Can't implement this unless we know the NTFS version in use
    #@staticmethod
    #def structure_size(buf, offset, parent):
    #    return 0x42 + (read_byte(buf, offset + 0x40) * 2)

    # Can't implement this unless we know the NTFS version in use
    #def __len__(self):
    #    return 0x42 + (self.filename_length() * 2)

    def owner_id(self):
        """
        This is an explicit method because it may not exist in OSes under Win2k

        @raises StandardInformationFieldDoesNotExist
        """
        try:
            return self.unpack_dword(0x30)
        except OverrunBufferException:
            raise StandardInformationFieldDoesNotExist("Owner ID")

    def security_id(self):
        """
        This is an explicit method because it may not exist in OSes under Win2k

        @raises StandardInformationFieldDoesNotExist
        """
        try:
            return self.unpack_dword(0x34)
        except OverrunBufferException:
            raise StandardInformationFieldDoesNotExist("Security ID")

    def quota_charged(self):
        """
        This is an explicit method because it may not exist in OSes under Win2k

        @raises StandardInformationFieldDoesNotExist
        """
        try:
            return self.unpack_dword(0x38)
        except OverrunBufferException:
            raise StandardInformationFieldDoesNotExist("Quota Charged")

    def usn(self):
        """
        This is an explicit method because it may not exist in OSes under Win2k

        @raises StandardInformationFieldDoesNotExist
        """
        try:
            return self.unpack_dword(0x40)
        except OverrunBufferException:
            raise StandardInformationFieldDoesNotExist("USN")


class FilenameAttribute(Block, Nestable):
    def __init__(self, buf, offset, parent):
        logging.debug("FILENAME ATTRIBUTE at %s.", hex(offset))
        super(FilenameAttribute, self).__init__(buf, offset)
        self.declare_field("qword", "mft_parent_reference", 0x0)
        self.declare_field("filetime", "created_time")
        self.declare_field("filetime", "modified_time")
        self.declare_field("filetime", "changed_time")
        self.declare_field("filetime", "accessed_time")
        self.declare_field("qword", "physical_size")
        self.declare_field("qword", "logical_size")
        self.declare_field("dword", "flags")
        self.declare_field("dword", "reparse_value")
        self.declare_field("byte", "filename_length")
        self.declare_field("byte", "filename_type")
        self.declare_field("wstring", "filename", 0x42, self.filename_length())

    @staticmethod
    def structure_size(buf, offset, parent):
        return 0x42 + (read_byte(buf, offset + 0x40) * 2)

    def __len__(self):
        return 0x42 + (self.filename_length() * 2)


class SlackIndexEntry(IndexEntry):
    def __init__(self, buf, offset, parent):
        """
        Constructor.
        Arguments:
        - `buf`: Byte string containing NTFS INDX file
        - `offset`: The offset into the buffer at which the block starts.
        - `parent`: The parent NTATTR_STANDARD_INDEX_HEADER block,
            which links to this block.
        """
        super(SlackIndexEntry, self).__init__(buf, offset, parent)

    def is_valid(self):
        # this is a bit of a mess, but it should work
        recent_date = datetime(1990, 1, 1, 0, 0, 0)
        future_date = datetime(2025, 1, 1, 0, 0, 0)
        try:
            fn = self.filename_information()
        except:
            return False
        if not fn:
            return False
        try:
            return fn.modified_time() > recent_date and \
                   fn.accessed_time() > recent_date and \
                   fn.changed_time() > recent_date and \
                   fn.created_time() > recent_date and \
                   fn.modified_time() < future_date and \
                   fn.accessed_time() < future_date and \
                   fn.changed_time() < future_date and \
                   fn.created_time() < future_date
        except ValueError:
            return False


class Runentry(Block, Nestable):
    def __init__(self, buf, offset, parent):
        super(Runentry, self).__init__(buf, offset)
        logging.debug("RUNENTRY @ %s.", hex(offset))
        self.declare_field("byte", "header")
        self._offset_length = self.header() >> 4
        self._length_length = self.header() & 0x0F
        self.declare_field("binary",
                           "length_binary",
                           self.current_field_offset(), self._length_length)
        self.declare_field("binary",
                           "offset_binary",
                           self.current_field_offset(), self._offset_length)

    @staticmethod
    def structure_size(buf, offset, parent):
        b = read_byte(buf, offset)
        return (b >> 4) + (b & 0x0F) + 1

    def __len__(self):
        return 0x1 + (self._length_length + self._offset_length)

    def is_valid(self):
        return self._offset_length > 0 and self._length_length > 0

    def lsb2num(self, binary):
        count = 0
        ret = 0
        for b in binary:
            ret += b << (8 * count)
            count += 1
        return ret

    def lsb2signednum(self, binary):
        count = 0
        ret = 0
        working = []

        is_negative = (binary[-1] & (1 << 7) != 0)
        if is_negative:
            working = [b ^ 0xFF for b in binary]
        else:
            working = [b for b in binary]
        for b in working:
            ret += b << (8 * count)
            count += 1
        if is_negative:
            ret += 1
            ret *= -1
        return ret

    def offset(self):
        # TODO(wb): make this run_offset
        return self.lsb2signednum(self.offset_binary())

    def length(self):
        # TODO(wb): make this run_offset
        return self.lsb2num(self.length_binary())


class Runlist(Block):
    def __init__(self, buf, offset, parent):
        super(Runlist, self).__init__(buf, offset)
        logging.debug("RUNLIST @ %s.", hex(offset))

    @staticmethod
    def structure_size(buf, offset, parent):
        length = 0
        while True:
            b = read_byte(buf, offset + length)
            length += 1
            if b == 0:
                return length

            length += (b >> 4) + (b & 0x0F)

    def __len__(self):
        return sum(map(len, self._entries()))

    def _entries(self, length=None):
        ret = []
        offset = self.offset()
        entry = Runentry(self._buf, offset, self)
        while entry.header() != 0 and \
              (not length or offset < self.offset() + length) and \
              entry.is_valid():
            ret.append(entry)
            offset += len(entry)
            entry = Runentry(self._buf, offset, self)
        return ret

    def runs(self, length=None):
        """
        Yields tuples (volume offset, length).
        Recall that the entries are relative to one another
        """
        last_offset = 0
        for e in self._entries(length=length):
            current_offset = last_offset + e.offset()
            current_length = e.length()
            last_offset = current_offset
            yield (current_offset, current_length)


class ATTR_TYPE:
    STANDARD_INFORMATION = 0x10
    FILENAME_INFORMATION = 0x30
    DATA = 0x80
    INDEX_ROOT = 0x90
    INDEX_ALLOCATION = 0xA0


class Attribute(Block, Nestable):
    TYPES = {
        16: "$STANDARD INFORMATION",
        32: "$ATTRIBUTE LIST",
        48: "$FILENAME INFORMATION",
        64: "$OBJECT ID/$VOLUME VERSION",
        80: "$SECURITY DESCRIPTOR",
        96: "$VOLUME NAME",
        112: "$VOLUME INFORMATION",
        128: "$DATA",
        144: "$INDEX ROOT",
        160: "$INDEX ALLOCATION",
        176: "$BITMAP",
        192: "$SYMBOLIC LINK",
        208: "$REPARSE POINT/$EA INFORMATION",
        224: "$EA",
        256: "$LOGGED UTILITY STREAM",
    }

    FLAGS = {
        0x01: "readonly",
        0x02: "hidden",
        0x04: "system",
        0x08: "unused-dos",
        0x10: "directory-dos",
        0x20: "archive",
        0x40: "device",
        0x80: "normal",
        0x100: "temporary",
        0x200: "sparse",
        0x400: "reparse-point",
        0x800: "compressed",
        0x1000: "offline",
        0x2000: "not-indexed",
        0x4000: "encrypted",
        0x10000000: "has-indx",
        0x20000000: "has-view-index",
        }

    def __init__(self, buf, offset, parent):
        super(Attribute, self).__init__(buf, offset)
        logging.debug("ATTRIBUTE @ %s.", hex(offset))
        self.declare_field("dword", "type")
        self.declare_field("dword", "size")  # this value must rounded up to 0x8 byte alignment
        self.declare_field("byte", "non_resident")
        self.declare_field("byte", "name_length")
        self.declare_field("word", "name_offset")
        self.declare_field("word", "flags")
        self.declare_field("word", "instance")
        if self.non_resident() > 0:
            self.declare_field("qword", "lowest_vcn", 0x10)
            self.declare_field("qword", "highest_vcn")
            self.declare_field("word", "runlist_offset")
            self.declare_field("byte", "compression_unit")
            self.declare_field("byte", "reserved1")
            self.declare_field("byte", "reserved2")
            self.declare_field("byte", "reserved3")
            self.declare_field("byte", "reserved4")
            self.declare_field("byte", "reserved5")
            self.declare_field("qword", "allocated_size")
            self.declare_field("qword", "data_size")
            self.declare_field("qword", "initialized_size")
            self.declare_field("qword", "compressed_size")
        else:
            self.declare_field("dword", "value_length", 0x10)
            self.declare_field("word", "value_offset")
            self.declare_field("byte", "value_flags")
            self.declare_field("byte", "reserved")
            self.declare_field("binary", "value",
                               self.value_offset(), self.value_length())

    @staticmethod
    def structure_size(buf, offset, parent):
        s = read_dword(buf, offset + 0x4)
        return s + (8 - (s % 8))

    def __len__(self):
        return self.size()

    def runlist(self):
        return Runlist(self._buf, self.offset() + self.runlist_offset(), self)

    def size(self):
        s = self.unpack_dword(self._off_size)
        return s + (8 - (s % 8))

    def name(self):
        return self.unpack_wstring(self.name_offset(), self.name_length())


class MFT_RECORD_FLAGS:
    MFT_RECORD_IN_USE = 0x1
    MFT_RECORD_IS_DIRECTORY = 0x2


def MREF(mft_reference):
    """
    Given a MREF/mft_reference, return the record number part.
    """
    return mft_reference & 0xFFFFFFFFFFFF


def MSEQNO(mft_reference):
    """
    Given a MREF/mft_reference, return the sequence number part.
    """
    return (mft_reference >> 48) & 0xFFFF


class MFTRecord(FixupBlock):
    """
    Implementation note: cannot be nestable due to fixups.
    """
    def __init__(self, buf, offset, parent, inode=None):
        super(MFTRecord, self).__init__(buf, offset, parent)
        logging.debug("MFTRECORD @ %s.", hex(offset))

        self.declare_field("dword", "magic")
        self.declare_field("word",  "usa_offset")
        self.declare_field("word",  "usa_count")
        self.declare_field("qword", "lsn")
        self.declare_field("word",  "sequence_number")
        self.declare_field("word",  "link_count")
        self.declare_field("word",  "attrs_offset")
        self.declare_field("word",  "flags")
        self.declare_field("dword", "bytes_in_use")
        self.declare_field("dword", "bytes_allocated")
        self.declare_field("qword", "base_mft_record")
        self.declare_field("word",  "next_attr_instance")
        self.declare_field("word",  "reserved")
        self.declare_field("dword", "mft_record_number")
        self.inode = inode or self.mft_record_number()

        self.fixup(self.usa_count(), self.usa_offset())

    def attributes(self):
        offset = self.attrs_offset()

        while self.unpack_dword(offset) != 0 and \
              self.unpack_dword(offset) != 0xFFFFFFFF and \
              offset + self.unpack_dword(offset + 4) <= self.offset() + self.bytes_in_use():
            a = Attribute(self._buf, offset, self)
            offset += len(a)
            yield a

    def attribute(self, attr_type):
        for a in self.attributes():
            if a.type() == attr_type:
                return a

    def is_directory(self):
        return self.flags() & MFT_RECORD_FLAGS.MFT_RECORD_IS_DIRECTORY

    def is_active(self):
        return self.flags() & MFT_RECORD_FLAGS.MFT_RECORD_IN_USE

    # this a required resident attribute
    def filename_information(self):
        """
        MFT Records may have more than one FN info attribute,
        each with a different type of filename (8.3, POSIX, etc.)

        This function returns the attribute with the most complete name,
          that is, it tends towards Win32, then POSIX, and then 8.3.
        """
        fn = None
        for a in self.attributes():
            # TODO optimize to self._buf here
            if a.type() == ATTR_TYPE.FILENAME_INFORMATION:
                try:
                    value = a.value()
                    check = FilenameAttribute(value, 0, self)
                    if check.filename_type() == 0x0001 or \
                       check.filename_type() == 0x0003:
                        return check
                    fn = check
                except Exception:
                    pass
        return fn

    # this a required resident attribute
    def standard_information(self):
        try:
            attr = self.attribute(ATTR_TYPE.STANDARD_INFORMATION)
            return StandardInformation(attr.value(), 0, self)
        except AttributeError:
            return None

    def data_attribute(self):
        """
        Returns None if the default $DATA attribute does not exist
        """
        for attr in self.attributes():
            if attr.type() == ATTR_TYPE.DATA and attr.name() == "":
                return attr

    def slack_data(self):
        """
        Returns A binary string containing the MFT record slack.
        """
        return self._buf[self.offset()+self.bytes_in_use():self.offset() + 1024].tostring()

    def active_data(self):
        """
        Returns A binary string containing the MFT record slack.
        """
        return self._buf[self.offset():self.offset() + self.bytes_in_use()].tostring()


class InvalidAttributeException(INDXException):
    def __init__(self, value=-1):
        super(InvalidAttributeException, self).__init__(value)

    def __str__(self):
        return "Invalid attribute Exception(%s)" % (self._value)


class InvalidMFTRecordNumber(Exception):
    def __init__(self, value=-1):
        self.value = value


class MFTOperationNotImplementedError(Exception):
    def __init__(self, msg=''):
        super(MFTOperationNotImplementedError, self).__init__(msg)
        self._msg = msg

    def __str__(self):
        return "MFTOperationNotImplemented(%s)" % (self._msg)


class InvalidRecordException(Exception):
    def __init__(self, msg=''):
        super(InvalidRecordException, self).__init__(msg)
        self._msg = msg

    def __str__(self):
        return "InvalidRecordException(%s)" % (self._msg)


class MFTEnumerator(object):

    DEFAULT_CACHE_SIZE = 1024

    CYCLE_ENTRY = '<CYCLE>'
    UNKNOWN_ENTRY = '??'
    ORPHAN_ENTRY = '$ORPHAN'
    FILE_SEP = os.pathsep

    def __init__(self, parent, stream,
                 record_cache=None, path_cache=None):
        self._parent = parent
        self._stream = stream
        self._record_cache = record_cache or Cache(self.DEFAULT_CACHE_SIZE)
        self._path_cache = path_cache or Cache(self.DEFAULT_CACHE_SIZE)

    def get_record_buf(self, record_num):
        start = (record_num * self._parent.bytes_per_mft_record
                 + self._parent.mft_abs_pos)
        self._stream.seek(start)

        return array.array('B', self._stream.read())

    def get_record(self, record_num):
        if self._record_cache.exists(record_num):
            self._record_cache.touch(record_num)

            return self._record_cache.get(record_num)

        record_buf = self.get_record_buf(record_num)
        if read_dword(record_buf, 0) != 0x454c4946: # magic FILE
            raise InvalidRecordException

        record = MFTRecord(record_buf, 0, False, inode=record_num)
        self._record_cache.insert(record_num, record)

        return record

    def enumerate_records(self):
        index = 0
        while True:
            if index == 12:
                index = 16
            try:
                record = self.get_record(index)
                yield record
                index += 1
            except MFTExhausted:
                return
            except InvalidRecordException:
                index += 1
                continue

    def enumerate_paths(self):
        for record in self.enumerate_records():
            path = self.get_path(record)
            yield record, path

    def get_path(self, record):
        return self._get_path_impl(record, set())

    def _get_path_impl(self, record, cycle_detector):
        key = "%d-%d-%d-%d-%d" % (record.magic(),
                                  record.lsn(),
                                  record.link_count(),
                                  record.mft_record_number(),
                                  record.flags())

        if self._path_cache.exists(key):
            self._path_cache.touch(key)

            return self._path_cache.get(key)

        record_num = record.mft_record_number()
        if record_num == 5:
            return ''

        if record_num in cycle_detector:
            return self.CYCLE_ENTRY
        cycle_detector.add(record_num)

        fn = record.filename_information()

        if not fn:
            return self.UNKNOWN_ENTRY
        else:
            record_filename = fn.filename()

        parent_record_num = MREF(fn.mft_parent_reference())
        parent_seq_num = MSEQNO(fn.mft_parent_reference())

        try:
            parent_record = self.get_record(parent_record_num)
        except (MFTExhausted, InvalidRecordException):
            return os.path.join(self.ORPHAN_ENTRY, record_filename)

        if parent_record.sequence_number() != parent_seq_num:
            return os.path.join(self.ORPHAN_ENTRY, record_filename)

        path = os.path.join(self._get_path_impl(parent_record, cycle_detector),
                            record_filename)
        self._path_cache.insert(key, path)

        return path

    def get_record_by_path(self, path):
        lower_path = path.lower()
        for record, record_path in self.enumerate_paths():
            if lower_path == record_path.lower():
                return record
        raise KeyError('Path not found: %s' % path)
