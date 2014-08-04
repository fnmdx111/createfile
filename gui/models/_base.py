# encoding: utf-8
from PySide.QtCore import *


class BaseFileModel(QAbstractItemModel):
    def __init__(self, parent):
        super().__init__(parent=parent)

        self._data = []
        self.headers = []

        self.checkbox_columns = set()

    def columnCount(self, parent=None):
        return len(self.headers)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]

    def index(self, row, column, parent=QModelIndex()):
        return self.createIndex(row, column)

    def parent(self, index):
        return self.createIndex(-1, -1)

    def rowCount(self, parent=None):
        return len(self._data)

    def clear(self):
        self.beginRemoveRows(QModelIndex(), 0, len(self._data) - 1)
        self._data.clear()
        self.endRemoveRows()

    def appendRow(self, data):
        self.beginInsertRows(QModelIndex(), len(self._data), len(self._data))
        self._data.append(data)
        self.endInsertRows()

    def sort(self, col, order=Qt.AscendingOrder):
        if not 0 <= col < self.columnCount():
            return

        self.beginResetModel()
        self._data.sort(key=lambda x: x[col],
                        reverse=order == Qt.DescendingOrder)
        self.endResetModel()
