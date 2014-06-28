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
    def __init__(self):
        self.default_read_buffer_size = 1024 * 4

    def set_default_read_buffer_size(self, size):
        """Set default read buffer size.

        :param size: default read buffer size to set.
        """

        self.default_read_buffer_size = size

    def read(self, size=None):
        """Read specified size from the image.

        :param size: optional, size to read.
        """

        size = size or self.default_read_buffer_size

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
