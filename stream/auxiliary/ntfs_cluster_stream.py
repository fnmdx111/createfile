# encoding: utf-8
"""
    stream.auxiliary.ntfs_cluster_stream
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements the convenience stream :class:`NTFSClusterStream` used
    in NTFS parsing.
"""
from io import BytesIO
import os
from struct import pack
from stream.read_only_stream import ReadOnlyStream

class CorruptedSector(BaseException):
    pass


class NTFSClusterStream(ReadOnlyStream):
    """
    NTFS cluster streams, which is mostly used in attribute discovery, modify the
    last two bytes (fixup) to real values according to the update sequence.
    """
    def __init__(self, raw, sector_size, update_seq):
        """
        :param raw: raw bytes read from real stream.
        :param sector_size: size of sectors.
        :param update_seq: update sequence.
        """

        super(NTFSClusterStream, self).__init__()

        fix_up, updates = update_seq[:2],\
                          (lambda _: (pack('BB', *p)
                                      for p in zip(*[_] * 2)))(
                              iter(update_seq[2:]))

        rd = BytesIO(raw)
        wr = BytesIO()
        while True:
            _ = rd.read(sector_size - 2)
            if not _:
                break

            wr.write(_)
            if rd.read(2) != fix_up:
                raise CorruptedSector
            else:
                wr.write(next(updates))

        self._stream = BytesIO(wr.getvalue())

    def read(self, size=None):
        if size is None:
            size = self.default_read_buffer_size

        return self._stream.read(size)

    def tell(self):
        return self._stream.tell()

    def seek(self, pos, whence=os.SEEK_SET):
        return self._stream.seek(pos, whence)

    def getvalue(self):
        return self._stream.getvalue()

    def set_update_seq(self, update_seq):
        pass
