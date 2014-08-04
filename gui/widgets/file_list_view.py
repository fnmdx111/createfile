# encoding: utf-8
from datetime import datetime
from PySide.QtGui import *
import time
from ..models.misc import long_str, extra_long_str, long_int


class FileListView(QTreeView):

    COLUMN_SIZE_UNIT = 35

    def __init__(self, parent, model):
        super().__init__(parent=parent)

        self.model_ = model

        self.parent_ = parent

        self.setSortingEnabled(True)

        self.setModel(self.model_)

        self.setItemsExpandable(False)
        self.setRootIsDecorated(False)
        self.setSelectionMode(QAbstractItemView.SingleSelection)

        for i, t in enumerate(self.model_.header_types):
            if t == bool:
                self.setColumnWidth(i, self.COLUMN_SIZE_UNIT)
            elif t == str:
                self.setColumnWidth(i, 3 * self.COLUMN_SIZE_UNIT)
            elif t == long_str:
                self.setColumnWidth(i, 7 * self.COLUMN_SIZE_UNIT)
            elif t == extra_long_str:
                self.setColumnWidth(i, 8 * self.COLUMN_SIZE_UNIT)
            elif t == int:
                self.setColumnWidth(i, int(1.5 * self.COLUMN_SIZE_UNIT))
            elif t == long_int:
                self.setColumnWidth(i, 2 * self.COLUMN_SIZE_UNIT)
            elif t == datetime:
                self.setColumnWidth(i, 4 * self.COLUMN_SIZE_UNIT)

    def clear(self):
        _1 = time.time()
        self.model_.clear()
        _2 = time.time()
        print('>>>> model clear costs %s' % (_2 - _1))

    def append(self, items):
        self.model_.appendRow(items)

    def remove(self, row_number):
        self.model_.removeRow(row_number)
