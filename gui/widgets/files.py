# encoding: utf-8
from PySide.QtGui import *

from . import FileListView
from ..models import FAT32FileModel, NTFSFileModel
from drive.fs.fat32 import FAT32



class FilesWidget(QDialog):
    def __init__(self, parent, partition_type):
        super().__init__(parent=parent)

        if partition_type == FAT32.type:
            self._flv = FileListView(self, FAT32FileModel(self))
        else:
            self._flv = FileListView(self, NTFSFileModel(self))

        _l = QVBoxLayout()
        _l.addWidget(self._flv)
        self.setLayout(_l)

    def model(self):
        return self._flv.model_

    def append(self, *args, **kwargs):
        self._flv.append(*args, **kwargs)

    def clear(self):
        self._flv.clear()
