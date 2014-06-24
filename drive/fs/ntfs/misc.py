# encoding: utf-8
"""
    drive.fs.ntfs.misc
    ~~~~~~~~~~~~~~~~~~

    This module implements miscellaneous functions useful for
    :package:`drive.fs.ntfs`.
"""
from datetime import datetime
from construct import Const, Bytes


id_ = lambda _: _
all_zero = lambda n: lambda s: Const(s, b'\x00' * n)
StrictlyUnused = lambda n: (all_zero(n) if STRICT else id_)(Bytes(None, n))
Unused = lambda n: Bytes(None, n)

STRICT = False

_local_time_delta = (datetime(year=1970, month=1, day=1) -
                     datetime(year=1601, month=1, day=1)).total_seconds()
_local_timestamp = lambda n: n / 10000000 - _local_time_delta
