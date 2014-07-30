# encoding: utf-8
from PySide.QtGui import *

from ._base import BaseSubWindow
from drive.fs.ntfs.plot import plot_sne1, plot_lsn
from ..misc import boolean_item, new_tool_button


class NTFSSubWindow(BaseSubWindow):
    def __init__(self, parent, partition, partition_address):
        super().__init__(parent, partition, partition_address)

        self.rules_widget.inflate_with_ntfs_rules()

    def deduce_abnormal_files(self, entries):
        return entries

    def plot_sne1(self):
        figure = plot_sne1(self.entries)

        self.add_figure(figure, label='SN = 1')

    def plot_lsn(self):
        figure = plot_lsn(self.entries)

        self.add_figure(figure, label='LSN')

    def plot_timeline(self):
        self._show_timeline('si_create_time',
                            True)

    def setup_related_buttons(self):
        btn_plot_sne1ct = new_tool_button('$SIC图', ':/plot.png')
        btn_plot_sne1ct.clicked.connect(self.plot_sne1)

        btn_plot_lsn = new_tool_button('LSN 图', ':/plot.png')
        btn_plot_lsn.clicked.connect(self.plot_lsn)

        btn_plot_timeline = new_tool_button('时间线', ':/timeline.png')
        btn_plot_timeline.clicked.connect(self.plot_timeline)

        group_box = QGroupBox('NTFS分析工具集')

        _ = QHBoxLayout()
        _.addWidget(btn_plot_sne1ct)
        _.addWidget(btn_plot_lsn)
        _.addWidget(btn_plot_timeline)

        group_box.setLayout(_)

        _ = QVBoxLayout()
        _.addWidget(group_box)

        return _

    def deduce_authentic_time(self, entries):
        return self._deduce_authentic_time(entries, 'si_create_time')

    def gen_file_row_data(self, row):
        return [boolean_item(row.abnormal),
                row.id,
                boolean_item(not row.is_deleted),
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
