# encoding: utf-8
from datetime import datetime
from PySide.QtCore import *
from ._base import BaseFileModel
from .misc import long_str, long_int, extra_long_str

from ..misc import SortableStandardItemModel, DataRole

class FAT32FileModel(BaseFileModel):
    def __init__(self, parent):
        super().__init__(parent=parent)

        self._data = []
        self.headers = ['编号', '选中', '异常',
                        'FDT编号',
                        '删除',
                        '路径',
                        '首簇号',
                        '尾簇号',
                        '创建时间',
                        '修改时间',
                        '访问日期',
                        '可用结论',
                        '异常报警来源',
                        '正确创建时间推测']
        self.header_types = [int,
                             bool, bool,
                             int,
                             bool,
                             long_str,
                             long_int, long_int,
                             datetime, datetime, datetime,
                             str, str, extra_long_str]

        self.checkbox_columns = {1, 2, 4}

    def flags(self, idx):
        row, col = idx.row(), idx.column()
        if (not idx.isValid()
            or not (0 <= row < self.rowCount())
            or not (0 <= col < self.columnCount())):
            return Qt.ItemIsEnabled

        if col == 1:
            return Qt.ItemFlags(super().flags(idx) | Qt.ItemIsUserCheckable)
        elif col in {}:
            return Qt.ItemFlags(super().flags(idx) & ~Qt.ItemIsEnabled)
        else:
            return Qt.ItemFlags(super().flags(idx))

    def data(self, idx, role=Qt.DisplayRole):
        row, col = idx.row(), idx.column()
        if (not idx.isValid()
            or not (0 <= row < self.rowCount())
            or not (0 <= col < self.columnCount())):
            return None

        if role == Qt.DisplayRole:
            if col in self.checkbox_columns:
                return None
            else:
                return str(self._data[row][col])
        elif role == Qt.CheckStateRole:
            if col in self.checkbox_columns:
                return Qt.Checked if self._data[row][col] else Qt.Unchecked
            else:
                return None
        elif role == SortableStandardItemModel.SortRole:
            return self.sort_types[col](self._data[row][col])
        elif role == DataRole:
            return self._data[row][col]

    def setData(self, idx, value, role):
        row, col = idx.row(), idx.column()
        if (not idx.isValid()
            or not (0 <= row < self.rowCount())
            or not (0 <= col < self.columnCount())):
            return None

        if role == Qt.CheckStateRole:
            self._data[row][col] = value == Qt.Checked
            return True

        return False
