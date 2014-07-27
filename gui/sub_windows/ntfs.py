# encoding: utf-8
from PySide.QtCore import *
from PySide.QtGui import *
from ._base import BaseSubWindow
from ..misc import abnormal_standard_item


class NTFSSubWindow(BaseSubWindow):


    def __init__(self, parent, partition, partition_address):
        super().__init__(parent, partition, partition_address)

        self.rules_widget.inflate_with_ntfs_rules()

    def deduce_abnormal_files(self, entries):
        return entries

    def setup_related_buttons(self):
        btn_plot_sne1ct = QPushButton('绘制sn = 1的MFT记录的$SI创建时间图')

        group_box = QGroupBox('NTFS分析工具集')

        _ = QVBoxLayout()
        _.addWidget(btn_plot_sne1ct)

        group_box.setLayout(_)

        _ = QVBoxLayout()
        _.addWidget(group_box)

        return _

    def deduce_authentic_time(self, entries):
        return self._deduce_authentic_time(entries, 'si_create_time')

    def gen_file_row_data(self, row):
        return [abnormal_standard_item(row),
                row.id,
                row.full_path,
                row.lsn, row.sn,
                row.first_cluster,
                row.si_create_time, row.si_modify_time,
                row.si_access_time, row.si_mft_time,
                row.fn_create_time, row.fn_modify_time,
                row.fn_access_time, row.fn_mft_time,
                row.conclusions,
                row.abnormal_src if 'abnormal_src' in row else '',
                row.deduced_time]
