# encoding: utf-8
import logging
from stream import ImageStream, WindowsPhysicalDriveStream

stream = ImageStream('d:/flash.raw')
address, port = '127.0.0.1', 8000

partition_log_level = logging.INFO
