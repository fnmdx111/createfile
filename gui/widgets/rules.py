# encoding: utf-8
from PySide.QtCore import *
from PySide.QtGui import *
from judge import *
from datetime import datetime, timedelta
from .column_list_view import ColumnListView


class RulesWidget(QWidget):

    _fat32_rules = [['_.create_time > _.modify_time', '复制']]
    _ntfs_rules = []

    def __init__(self, parent):
        super(RulesWidget, self).__init__(parent=parent)

        self._clv = ColumnListView(['已启用', '规则', '结论'], parent)

        self._setup_layout()

    def _inflate_rules(self, which_rules, clear):
        if clear:
            self._clv.clear()

        for r, c in which_rules:
            self._clv.append(['', r, c], checkable=True)

    def inflate_with_fat32_rules(self, clear=True):
        self._inflate_rules(self._fat32_rules, clear)

    def inflate_with_ntfs_rules(self, clear=True):
        self._inflate_rules(self._ntfs_rules, clear)

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

            if on.checkState() == Qt.Checked:
                yield If(eval(rule.text())).then(conclusion=conclusion.text())
