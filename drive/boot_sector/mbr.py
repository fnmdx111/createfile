# encoding: utf-8
"""
    drive.boot_sector.mbr
    ~~~~~~~~~~~~~~~~~~~~~

    This module defines the classical main boot record (MBR).
"""
from ._boot_sector import boot_sector_template

ClassicalMBR = boot_sector_template(0)
