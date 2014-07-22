# encoding: utf-8
from PySide.QtGui import *
from PySide.QtCore import *
from ..widgets import ColumnListView
from stats import windowed


class AuthenticCreateTimeDeductionDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent=parent)

        self.parent_ = parent

        self._clv = ColumnListView(['文件编号', '首簇',
                                    '创建时间', '正确时间推测'],
                                   self)
        _l = QVBoxLayout()
        _l.addWidget(self._clv)
        self.setLayout(_l)

        self.setWindowFlags(self.windowFlags() |
                            Qt.WindowMaximizeButtonHint)

        self.setModal(False)

        self._title = '正确时间推测'

    def deduct(self):
        abnormal_file_numbers = self.parent_.abnormal_file_numbers

        entries = self.parent_.filter_entries()
        if entries is None:
            return

        entries = list(map(lambda _: _[1],
                           entries.iterrows()))
        abnormal_files = list(map(lambda _: (_, entries[_]),
                                  abnormal_file_numbers))

        self._clv.clear()

        visited_files = set()
        _buf = []

        for i, af in abnormal_files:
            if af.first_cluster < entries[0].first_cluster:
                if i not in visited_files:
                    _buf.append([i,
                                 af.first_cluster,
                                 af.create_time,
                                 '%s之前' % entries[0].create_time])
                    visited_files.add(i)

        for entry2, entry1 in windowed(list(reversed(entries)), size=2):
            for i, af in abnormal_files:
                if (entry1.first_cluster
                 <= af.first_cluster
                 < entry2.first_cluster):
                    if i not in visited_files:
                        _buf.append([i, af.first_cluster,
                                     af.create_time,
                                     '%s与%s之间' % (entry1.create_time,
                                                  entry2.create_time)])
                        visited_files.add(i)

        for i, af in abnormal_files:
            if entries[-1].first_cluster <= af.first_cluster:
                if i not in visited_files:
                    _buf.append([i, af.first_cluster,
                                 af.create_time,
                                 '%s之后' % entries[-1].create_time])
                    visited_files.add(i)

        for items in sorted(_buf, key=lambda x: x[0]):
            self._clv.append(items)

    def show(self, *args, **kwargs):
        self.setWindowTitle('%s | 共%s个可疑文件' % (
            self._title,
            len(self.parent_.abnormal_file_numbers)
        ))

        return super().show(*args, **kwargs)
