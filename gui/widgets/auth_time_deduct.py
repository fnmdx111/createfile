# encoding: utf-8
from PySide.QtGui import *

from ..widgets import ColumnListView


class AuthenticTimeDeductionWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent=parent)

        self.parent_ = parent

        self._clv = ColumnListView(['文件编号', '首簇',
                                    '创建时间', '正确时间推测'],
                                   self)
        _l = QVBoxLayout()
        _l.addWidget(self._clv)
        self.setLayout(_l)


