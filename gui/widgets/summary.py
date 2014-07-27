# encoding: utf-8
from collections import defaultdict
from PySide.QtGui import *
from drive.fs.fat32 import FAT32

class SummaryWidget(QWidget):
    def __init__(self, parent, partition_type):
        super().__init__(parent=parent)

        self.label = QLabel()
        _l = QVBoxLayout()
        _l.addWidget(self.label)
        self.setLayout(_l)

        self.start_time = None
        self.end_time = None

        self.conclusions = defaultdict(int)

        self.partition_type = partition_type

        self.summary_text = ''

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
        self.summary_text = ''

    def set_summary(self, summary=''):
        s = summary or self.summary_text

        self.label.setText(s)

    def summarize(self, entries):
        self.clear()

        if self.partition_type == FAT32.type:
            st = min(entries['create_time'].min(),
                     entries['modify_time'].min(),
                     entries['access_date'].min())
            et = max(entries['create_time'].max(),
                     entries['modify_time'].max(),
                     entries['access_date'].max())
        else:
            st = entries.iloc[0]['si_create_time']
            et = entries.iloc[0]['si_create_time']
            for prefix in ['fn', 'si']:
                for ctg in ['create', 'modify', 'access', 'mft']:
                    name = '%s_%s_time' % (prefix, ctg)
                    st = min(entries[name].min(), st)
                    et = max(entries[name].max(), et)
        self.set_start_time(st)
        self.set_end_time(et)

        for _, item in entries.iterrows():
            for c in item.conclusions:
                self.conclusions[c] += 1

        t = ('分区使用起始时间：%s\n'
             '分区使用结束时间：%s\n' % (self.start_time,
                                        self.end_time))

        if self.conclusions:
            t += '在这期间中\n'
            for c, n in self.conclusions.items():
                t += '\t有%s次%s' % (n, c)

        self.summary_text = t

        return self.summary_text
