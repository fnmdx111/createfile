# encoding: utf-8
"""
    stream.read_only_stream
    ~~~~~~~~~~~~~~~~~

    This module implements the abstract class :class:`ReadOnlyStream`.
"""
import os


class ReadOnlyStream:
    """
    Abstract class for read-only streams.
    """
    DEFAULT_READ_BUFFER_SIZE = 1024 * 4

    def __init__(self):
        pass

    def read(self, size=DEFAULT_READ_BUFFER_SIZE):
        """Read specified size from the image.

        :param size: optional, size to read."""

        raise NotImplementedError

    def seek(self, pos, whence=os.SEEK_SET):
        """Seek to a specified position.

        :param pos: position to seek.
        :param whence: optional, seek mode.
        """

        raise NotImplementedError

    def tell(self):
        """Get current position."""

        raise NotImplementedError

    def close(self):
        """Close the stream."""

        raise NotImplementedError

    def test(self):
        """Tests if the stream is functional."""

        print(self.read(512).encode('hex'))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
