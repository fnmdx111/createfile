# encoding: utf-8
import os
from misc import MFTExhausted, InvalidRecordException

from ..read_only_stream import ReadOnlyStream



class MFTStream(ReadOnlyStream):
    def __init__(self, stream, parent, abs_lcn, mft_abs_pos, mft_size=1024):
        super().__init__()

        stream.seek(mft_abs_pos)

        self.parent = parent

        self._stream = stream
        self.mft_size = mft_size

        self.abs_lcn = abs_lcn

        self._data_runs = None
        self._lcn = 0
        self._current_rest_run_size = 0

        self._counter = 0

    def read(self, size=None):
        if size is not None:
            raise ValueError

        return self._read_record()

    def seek(self, pos, whence=os.SEEK_SET):
        self._stream.seek(pos, whence)

    def _read_record(self):
        if not self._data_runs:
            # read $MFT
            signature = self._stream.read(4)
            if signature not in [b'FILE', b'BAAD', b'INDX']:
                raise ValueError

            return b''.join([signature,
                             self._stream.read(self.mft_size - 4)])
        else:
            if self._current_rest_run_size == 0:
                try:
                    lcn, length = next(self._data_runs)
                    self._lcn += lcn
                    self._stream.seek(self.abs_lcn(self._lcn))
                    self._current_rest_run_size = length * (
                        self.parent.bytes_per_cluster / self.mft_size
                    )
                except StopIteration:
                    raise MFTExhausted

            self._current_rest_run_size -= 1

            signature = self._stream.read(4)
            if signature != b'FILE':
                raise InvalidRecordException

            return b''.join([signature,
                             self._stream.read(self.mft_size - 4)])

    def set_data_runs(self, data_runs_generator):
        self._data_runs = data_runs_generator
