# encoding: utf-8
"""
    drive.fs.__init__
    ~~~~~~~~~~~~~~~~~

    This module implements the abstract class :class:`Partition`.
"""
import logging
from misc import SimpleCounter

counters = {
    'FAT32': SimpleCounter(),
    'NTFS': SimpleCounter()
}

class Partition:
    """
    Abstract class which represents partitions.
    """
    def __init__(self, type_, stream, preceding_bytes, boot_sector_parser):
        """
        :param type_: type of the partition, e.g. FAT32.
        :param stream: stream to parse against.
        :param preceding_bytes: starting position of this partition,
        :param boot_sector_parser: parser which parses the boot sector of this
                                   partition.
        """

        self.type = type_

        self.preceding_bytes = preceding_bytes

        self.stream = stream

        self.logger = None
        self.setup_logger()

        self.logger.info('reading boot sector')
        self.boot_sector = boot_sector_parser(stream)

    def setup_logger(self):
        self.logger = logging.getLogger('%s|%s' % (self.type,
                                                     counters[self.type]))
        counters[self.type].inc()

        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s: %(message)s'
        ))
        self.logger.addHandler(handler)
