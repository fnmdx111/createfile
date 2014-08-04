# encoding: utf-8
from PySide.QtCore import *
from PySide.QtGui import *
import time
from ..misc import SortableStandardItemModel


class FileListView(QTreeView):
    def __init__(self, parent, model):
        super().__init__(parent=parent)

        self.model_ = model

        self.parent_ = parent

        self.setSortingEnabled(True)
        # self.proxy = QSortFilterProxyModel(parent)
        # self.proxy.setSortRole(SortableStandardItemModel.SortRole)
        # self.proxy.setSourceModel(self.model_)
        # self.setModel(self.proxy)
        self.setModel(self.model_)

        self.setItemsExpandable(False)
        self.setRootIsDecorated(False)
        self.setSelectionMode(QAbstractItemView.SingleSelection)

    def clear(self):
        _1 = time.time()
        self.model_.clear()
        _2 = time.time()
        print('>>>> model clear costs %s' % (_2 - _1))

    def append(self, items):
        self.model_.appendRow(items)

    def remove(self, row_number):
        self.model_.removeRow(row_number)
