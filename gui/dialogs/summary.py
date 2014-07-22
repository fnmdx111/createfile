# encoding: utf-8
from collections import defaultdict
from PySide.QtGui import *
from drive.fs.fat32 import FAT32
from drive.fs.ntfs import NTFS

class SummaryDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent=parent)

        self.label = QLabel()
        _l = QVBoxLayout()
        _l.addWidget(self.label)
        self.setLayout(_l)

        self.setWindowTitle('分区概要')

        self.start_time = None
        self.end_time = None

        self.conclusions = defaultdict(int)

    def set_start_time(self, start_time):
        self.start_time = start_time

    def set_end_time(self, end_time):
        self.end_time = end_time

    def add_conclusion(self, conclusion, n):
        self.conclusions[conclusion] = n

    def clear(self):
        self.start_time = None
        self.end_time = None
        self.conclusions.clear()

    def show(self, *args, **kwargs):
        def _slot(entries):
            if self.parent().partition_dialog.current_partition().type ==\
                    FAT32.type:
                st = min(entries['create_time'].min(),
                         entries['modify_time'].min(),
                         entries['access_date'].min())
                et = max(entries['create_time'].max(),
                         entries['modify_time'].max(),
                         entries['access_date'].max())
            else:
                st = entries[0]['si_create_time'].min()
                et = entries[0]['si_create_time'].max()
                for prefix in ['fn', 'si']:
                    for ctg in ['create', 'modify', 'access', 'mft']:
                        name = '%s_%s_time' % (prefix, ctg)
                        st = min(entries[name].min(), st)
                        et = max(entries[name].max(), et)
            self.set_start_time(st)
            self.set_end_time(et)

            _, result = self.parent().apply_rules(entries)
            for item in result:
                if item.conclusions:
                    for c in item.conclusions:
                        self.conclusions[c] += 1

            t = ('分区使用起始时间：%s\n'
                 '分区使用结束时间：%s\n' % (self.start_time,
                                            self.end_time))

            if self.conclusions:
                t += '在这期间中\n'
                for c, n in self.conclusions.items():
                    t += '\t有%s次%s操作' % (n, c)

            self.label.setText(t)

            return super(SummaryDialog, self).show(*args, **kwargs)

        self.parent().parse_partition(_slot,
                                      show_file_dialog_=False)
