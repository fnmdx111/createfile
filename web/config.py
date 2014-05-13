# encoding: utf-8
from drive.disk import get_drive_obj
from drive.fs.fat32 import FAT32
from stream import ImageStream, WindowsPhysicalDriveStream

stream = ImageStream('d:/flash.raw')
address, port = '127.0.0.1', 8000

