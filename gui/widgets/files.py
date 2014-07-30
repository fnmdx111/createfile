# encoding: utf-8
from datetime import datetime

from PySide.QtGui import *

from ..widgets import ColumnListView
from drive.fs.fat32 import FAT32
from drive.fs.ntfs import NTFS


class FilesWidget(QDialog):
    def __init__(self, parent):
        super().__init__(parent=parent)

        self._clv = ColumnListView(['路径'],
                                   self,
                                   headers_fit_content=False,
                                   order_column=True,
                                   sortable=True)
        self.setup_headers_by(self.parent().partition.type)

        _l = QVBoxLayout()
        _l.addWidget(self._clv)
        self.setLayout(_l)

    def append(self, *args, **kwargs):
        self._clv.append(*args, **kwargs)

    def setup_headers_by(self, type_):
        if type_ == FAT32.type:
            self._clv.setup_headers(['异常',
                                     'FDT编号',
                                     '已删除',
                                     '路径',
                                     '首簇号',
                                     '尾簇号',
                                     '创建时间',
                                     '修改时间',
                                     '访问日期',
                                     '可用结论',
                                     '异常报警来源',
                                     '正确创建时间推测'],
                                    size_hints=[0, 1, 3],
                                    sort_types=[bool,
                                                int,
                                                str,
                                                int, int,
                                                datetime, datetime, datetime,
                                                str, str, str])
        elif type_ == NTFS.type:
            self._clv.setup_headers(['异常',
                                     'MFT记录编号',
                                     '活动',
                                     '路径',
                                     'LSN',
                                     'SN',
                                     '首LCN',
                                     '$SI 创建时间',
                                     '$SI 修改时间',
                                     '$SI 访问时间',
                                     '$SI MFT修改时间',
                                     '$FN 创建时间',
                                     '$FN 修改时间',
                                     '$FN 访问时间',
                                     '$FN MFT修改时间',
                                     '可用结论',
                                     '异常报警来源',
                                     '正确创建时间推测'],
                                    sort_types=[bool, int, str, int, int, int,
                                                datetime, datetime,
                                                datetime, datetime,
                                                datetime, datetime,
                                                datetime, datetime,
                                                str, str, str])

    def clear(self):
        self._clv.clear()
