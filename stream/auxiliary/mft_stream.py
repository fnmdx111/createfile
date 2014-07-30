# encoding: utf-8
import os

from ..read_only_stream import ReadOnlyStream


class MFTExhausted(BaseException):
    pass


class MFTStream(ReadOnlyStream):
    def __init__(self, stream, mft_abs_pos, mft_size=1024):
        super().__init__()

        stream.seek(mft_abs_pos)

        self._stream = stream
        self.mft_size = mft_size

    def read(self, size=None):
        if size is not None:
            raise ValueError

        signature = self._stream.read(4)
        if signature not in [b'FILE', b'BAAD', b'INDX']:
            raise MFTExhausted

        return b''.join([signature,
                         self._stream.read(self.mft_size - 4)])

    def seek(self, pos, whence=os.SEEK_SET):
        self._stream.seek(pos, whence)
