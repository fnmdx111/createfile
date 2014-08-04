# encoding: utf-8
from PySide.QtGui import *
from PySide.QtCore import *
import time

from ..misc import SortableStandardItemModel


class ColumnListView(QTreeView):
    def __init__(self, headers, parent, model=None,
                 order_column=False,
                 headers_fit_content=False,
                 sortable=False,
                 sort_types=None):
        super(ColumnListView, self).__init__(parent)

        self.headers_ = headers

        self.setUniformRowHeights(True)

        self.parent_ = parent

        self.setItemsExpandable(False)
        self.setRootIsDecorated(False)
        self.setSelectionMode(QAbstractItemView.SingleSelection)

        if headers_fit_content:
            self.header().setResizeMode(QHeaderView.ResizeToContents)

        self.sortable = sortable
        self.sort_types = sort_types
        if sortable:
            self.setSortingEnabled(True)

            self.model_ = model or SortableStandardItemModel(parent, sort_types)

            self.sort_types = sort_types

            self.proxy = QSortFilterProxyModel(parent)
            self.proxy.setSortRole(SortableStandardItemModel.SortRole)
            self.proxy.setSourceModel(self.model_)

            self.setModel(self.proxy)
        else:
            self.proxy = None

            self.model_ = model or QStandardItemModel(parent)

            self.setModel(self.model_)

        self.order_column = order_column
        self.count = 0

        self.do_not_setup_headers = True
        if not model:
            self.do_not_setup_headers = False
            self.setup_headers()

    def setup_headers(self, headers=None, size_hints=(), sort_types=None):
        self.headers_ = headers or self.headers_

        if self.sortable:
            if sort_types:
                self.sort_types = sort_types
                if self.order_column:
                    self.sort_types.insert(0, int)

                self.model_.sort_types = self.sort_types

        if self.order_column:
            if self.headers_[0] != '编号':
                self.headers_.insert(0, '编号')
            self.header().setResizeMode(0, QHeaderView.ResizeToContents)

        for hint in size_hints:
            if self.order_column:
                hint += 1
            self.header().setResizeMode(hint, QHeaderView.ResizeToContents)

        self.model_.setHorizontalHeaderLabels(self.headers_)

    def clear(self):
        _1 = time.time()
        self.model_.clear()
        _2 = time.time()
        print('>>>> model clear costs %s' % (_2 - _1))

        self.count = 0

        if self.do_not_setup_headers:
            return

        _1 = time.time()
        self.setup_headers()
        _2 = time.time()
        print('>>>> headers setup costs %s' % (_2 - _1))

    def append(self, items, editable=False, checkable=False):
        if self.do_not_setup_headers:
            self.model_.appendRow(items)

            return

        def new_item(item, editable=editable, checkable=checkable):
            if isinstance(item, QStandardItem):
                return item

            _ = QStandardItem(str(item))
            _.setEditable(editable)
            _.setCheckable(checkable)
            if checkable:
                _.setCheckState(Qt.Checked)

            return _

        if checkable:
            _ = [new_item('', checkable=True)]
            _.extend([new_item(i, checkable=False) for i in items[1:]])
        else:
            _ = [new_item(i) for i in items]

        if self.order_column:
            _.insert(0, new_item(self.count, editable=False, checkable=False))

        self.model_.appendRow(_)
        self.count += 1

    def remove(self, row_number):
        if 0 <= row_number < self.model_.rowCount():
            self.model_.removeRow(row_number)

    def resize_columns(self):
        for i, _ in enumerate(self.headers_):
            self.resizeColumnToContents(i)
