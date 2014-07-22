# encoding: utf-8
from PySide.QtGui import *
from PySide.QtCore import *
from ..widgets import ColumnListView
from drive.fs.fat32 import FAT32
from drive.fs.ntfs import NTFS


class FilesDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent=parent)

        self._title = '文件列表'

        self.setModal(False)

        self.setWindowFlags(self.windowFlags() |
                            Qt.WindowMaximizeButtonHint)

        self._clv = ColumnListView(['路径'],
                                   self,
                                   order_column=True)
        _l = QVBoxLayout()
        _l.addWidget(self._clv)
        self.setLayout(_l)

    def show(self, *args, **kwargs):
        self.setWindowTitle('%s | %s个文件' % (self._title,
                                               self._clv.model_.rowCount()))
        return super().show(*args, **kwargs)

    def append(self, *args, **kwargs):
        self._clv.append(*args, **kwargs)

    def setup_headers_by(self, type_, additional_headers=None):
        if type_ == FAT32.type:
            self._clv.setup_headers(['路径',
                                     '首簇',
                                     '创建时间',
                                     '修改时间',
                                     '访问时间'] +
                                    (additional_headers or []))
        elif type_ == NTFS.type:
            self._clv.setup_headers(['路径',
                                     'LSN',
                                     'SN',
                                     '首VCN',
                                     '$SI 创建时间',
                                     '$SI 修改时间',
                                     '$SI 访问时间',
                                     '$SI MFT修改时间',
                                     '$FN 创建时间',
                                     '$FN 修改时间',
                                     '$FN 访问时间',
                                     '$FN MFT修改时间'] +
                                    (additional_headers or []))

    def clear(self):
        self._clv.clear()
