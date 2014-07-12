# encoding: utf-8
"""
    drive.boot_sector._boot_sector
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements the meta struct of the various boot sectors.
"""
from construct import *
from drive.boot_sector.misc import supported_partition_types
from ..keys import *
from misc import MAGIC_END_SECTION


def calc_chs_address(key):
    """Return a function that calculates the cluster-head-sector address
    (CHS address).

    :param key: key of the value to calculate against.
    """

    def _(context):
        """Calculate the CHS address.

        :param context: the context object.
        """

        h, s, c = context[key]

        head = h
        sector = 0b111111 & s
        cylinder = (0b11000000 & s) << 2 | c

        return cylinder, head, sector
    return _


def _partition_entry_template(abs_pos):
    """Generate a generic template for partition entry.

    :param abs_pos: absolute position of the boot sector where this entry
                    resides.
    """

    return Struct(k_PartitionEntry,
        # status is not needed so we don't parse this attribute
        Byte(k_status),

        # chs address is useful when locating certain partitions
        Array(3, ULInt8(k_starting_chs_address)),
        # parse them into a 3-tuple now
        Value(k_starting_chs_address,
              calc_chs_address(k_starting_chs_address)),

        Byte(k_partition_type),
        Value(k_partition_type, lambda c: supported_partition_types.get(
            c[k_partition_type],
            str(c[k_partition_type]
        ))),

        Array(3, ULInt8(k_ending_chs_address)),
        Value(k_ending_chs_address,
              calc_chs_address(k_ending_chs_address)),

        ULInt32(k_first_sector_address),
        Value(k_first_byte_address, # this is an absolute address
              lambda c: c[k_first_sector_address] * 512 + abs_pos),
        ULInt32(k_number_of_sectors),

        allow_overwrite=True
    )

def boot_sector_template(abs_pos):
    """Generate a generic template for other boot sectors.

    :param abs_pos: absolute position of the boot sector.
    """

    return Struct(k_MBR,
        # bootstrap code is not parsed for its less importance
        Bytes(None, 0x1be),

        # rename PartitionEntry to its plural form
        Rename(k_PartitionEntries,
               Array(4, _partition_entry_template(abs_pos))),

        Magic(MAGIC_END_SECTION)
    )
