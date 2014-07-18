# encoding: utf-8

from PySide.QtCore import *
from PySide.QtGui import *
from judge import *


class ColumnListView(QTreeView):
    def __init__(self, headers, parent, headers_fit_content=False):
        super(ColumnListView, self).__init__(parent)

        self.headers_ = headers

        self.model_ = QStandardItemModel(parent)
        self.setModel(self.model_)

        self.setItemsExpandable(False)
        self.setRootIsDecorated(False)
        self.setSelectionMode(QAbstractItemView.SingleSelection)

        self.setup_headers()
        if headers_fit_content:
            self.header().setResizeMode(QHeaderView.ResizeToContents)

    def setup_headers(self, headers=None):
        self.headers_ = headers or self.headers_
        self.model_.setHorizontalHeaderLabels(self.headers_)

    def clear(self):
        self.model_.clear()
        self.setup_headers()

    def append(self, items, editable=False, checkable=False):
        def new_item(item, editable=editable, checkable=checkable):
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

        self.model_.appendRow(_)

    def remove(self, row_number):
        if 0 <= row_number < self.model_.rowCount():
            self.model_.removeRow(row_number)

    def resize_columns(self):
        for i, _ in enumerate(self.headers_):
            self.resizeColumnToContents(i)


class RulesWidget(QWidget):
    def __init__(self, parent):
        super(RulesWidget, self).__init__(parent=parent)

        self._clv = ColumnListView(['已启用', '规则', '结论'], parent)
        self._clv.append(['', '_.create_time < _.modify_time', '复制'],
                         checkable=True)

        self._setup_layout()

    def _setup_layout(self):
        btn_add = QPushButton('添加')
        btn_remove = QPushButton('移除')

        le_rule = QLineEdit()
        _label = QLabel('=>')
        le_conclusion = QLineEdit()

        def add():
            self._clv.append(['', le_rule.text(), le_conclusion.text()],
                             checkable=True)
            le_rule.setText('')
            le_conclusion.setText('')
        btn_add.clicked.connect(add)

        def remove():
            self._clv.remove(self._clv.currentIndex().row())
        btn_remove.clicked.connect(remove)

        _l = QHBoxLayout()
        _l.addWidget(_label)
        _l.addWidget(le_conclusion)

        input_layout = QGridLayout()
        input_layout.addWidget(le_rule,    0, 0, 1, 1)
        input_layout.addLayout(_l,         1, 0, 1, 1)
        input_layout.addWidget(btn_add,    0, 1, 1, 1)
        input_layout.addWidget(btn_remove, 1, 1, 1, 1)

        layout = QVBoxLayout()
        layout.addLayout(input_layout)
        layout.addWidget(self._clv)

        self.setLayout(layout)

    def rules(self):
        for r in range(self._clv.model_.rowCount()):
            on, rule, conclusion = (self._clv.model_.item(r, 0),
                                    self._clv.model_.item(r, 1),
                                    self._clv.model_.item(r, 2))

            if on:
                yield If(eval(rule.text())).then(conclusion=conclusion.text())
