# encoding: utf-8
import os

from PySide.QtCore import *
from PySide.QtGui import *

from drive.boot_sector.misc import supported_partition_types
from drive.utils import discover_physical_drives, get_partition_table, \
    get_partition_obj
from ..misc import AsyncTaskMixin, human_readable, error_box, new_button, \
    warning_box
from stream import ImageStream, WindowsPhysicalDriveStream
from ..widgets import ColumnListView
from drive.keys import *


class PartitionsDialog(QDialog, AsyncTaskMixin):

    signal_partition_read = Signal(int, str, object)
    signal_wpd_loaded = Signal(list)
    signal_partition_loaded = Signal(object, int)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.setup_mixin(parent=kwargs['parent'])

        self.original_title = '选择分区'
        self.setWindowTitle(self.original_title)

        self._lw_wpd = QListWidget()
        self._clv_partitions = ColumnListView(['类型',
                                               '起始扇区',
                                               '大小',
                                               '扇区数'],
                                              self,
                                              headers_fit_content=True,
                                              order_column=True)

        self._current_stream = None
        self._partition_table = []
        self._current_partition = None

        self._stream_type, self._stream_arg = '', None

        self._setup_layout()
        self._setup_connections()

    def _setup_connections(self):
        def _partition_read(i, t, p):
            size = p[k_number_of_sectors] * p.get(k_bytes_per_sector, 512)

            self._clv_partitions.append([t,
                                         p.get(k_first_sector_address, 0),
                                         human_readable(size),
                                         p[k_number_of_sectors]])
            self._partition_table.append(p)

        self.signal_partition_read.connect(_partition_read)

        self.signal_wpd_loaded.connect(self._fill_in_wpd_view)

        self._p_selection_model = self._clv_partitions.selectionModel()
        self._p_selection_model.currentChanged.connect(self._load_partition)

        self.signal_partition_loaded.connect(self._set_current_partition)

    def _setup_layout(self):
        le_image_path = QLineEdit()
        label = QLabel('镜像路径：')
        label.setBuddy(le_image_path)

        def open_image():
            path, _ = QFileDialog.getOpenFileName(self,
                                                  '打开镜像文件',
                                                  '.',
                                                  '所有文件 (*.*)')
            le_image_path.setText(path if path else le_image_path.text())

        def load_image():
            if not le_image_path.text():
                return

            if self._current_stream:
                self._current_stream.close()

            path = le_image_path.text()
            if not os.path.exists(path):
                error_box(self, '路径不存在。')
                return

            self._current_stream = ImageStream(le_image_path.text())
            self._stream_type = ImageStream
            self._stream_arg = le_image_path.text()

            self._load_partitions()

        _l0 = QHBoxLayout()
        _l0.addWidget(label)
        _l0.addWidget(le_image_path)

        _l1 = QHBoxLayout()
        _l1.addWidget(new_button('打开...',
                                 open_image))
        _l1.addWidget(new_button('载入',
                                 load_image))

        _l2 = QVBoxLayout()
        _l2.addLayout(_l0)
        _l2.addLayout(_l1)

        img_group_box = QGroupBox('使用镜像文件')
        img_group_box.setLayout(_l2)

        self._lw_wpd.currentItemChanged.connect(self._wpd_changed)

        _l = QVBoxLayout()
        _l.addWidget(new_button('刷新', self._load_wpd))
        _l.addWidget(self._lw_wpd)

        wpd_group_box = QGroupBox('使用物理设备')
        wpd_group_box.setLayout(_l)

        _l = QVBoxLayout()
        _l.addWidget(self._clv_partitions)
        _l.addWidget(new_button('确定',
                                lambda: self.accept()))

        partitions_group_box = QGroupBox('已发现的分区')
        partitions_group_box.setLayout(_l)

        grid_layout = QGridLayout()
        grid_layout.addWidget(img_group_box,        0, 0, 1, 1)
        grid_layout.addWidget(wpd_group_box,        1, 0, 1, 1)
        grid_layout.addWidget(partitions_group_box, 0, 1, 2, 1)

        self.setLayout(grid_layout)

    def _load_wpd(self):
        self._lw_wpd.clear()

        def _():
            numbers = discover_physical_drives()
            self.signal_wpd_loaded.emit(numbers)

        self.do_async_task(_, title_before='正在载入物理驱动器...')

    def _wpd_changed(self, current, _):
        if not current:
            return

        self._p_selection_model.clearSelection()

        if self._current_stream:
            self._current_stream.close()

        arg = current.text().lstrip(r'\\.\PhysicalDrive\ ')
        self._current_stream = WindowsPhysicalDriveStream(arg)
        self._stream_type = WindowsPhysicalDriveStream
        self._stream_arg = arg

        self._load_partitions()

    def _fill_in_wpd_view(self, numbers):
        for n in numbers:
            QListWidgetItem(QFileIconProvider().icon(QFileIconProvider.Drive),
                            r'\\.\PhysicalDrive\%s' % n,
                            self._lw_wpd)

    def _load_partitions(self):
        self._clv_partitions.clear()
        self._partition_table = []

        def _():
            for i, p in enumerate(get_partition_table(self._current_stream)):
                if k_partition_type in p:
                    type_ = p[k_partition_type]
                else:
                    type_ = str(p[k_OEM_name], 'ascii')

                if 'NTFS' in type_:
                    type_ = 'NTFS'
                elif 'MSDOS' in type_:
                    type_ = 'FAT32'
                elif type_ == k_ignored:
                    continue

                self.signal_partition_read.emit(i, type_, p)

        self.do_async_task(_,
                           title_before='正在载入分区表...')

    def _load_partition(self, current_idx, _):
        row = current_idx.row()
        if row == -1:
            return
        elif not 0 <= row < len(self._partition_table):
            warning_box(self,
                        '未选择可用的分区。')
            return

        entry = self._partition_table[row]

        if k_partition_type in entry:
            if isinstance(entry[k_partition_type], int) and\
               entry[k_partition_type] not in supported_partition_types:
                error_box(self,
                          '不支持所选的分区类型（类型：%s）' %
                          entry[k_partition_type])
                return
        elif k_OEM_name in entry:
            entry[k_first_byte_address] = 0

            type_ = str(entry[k_OEM_name], 'ascii')
            if 'NTFS' in type_:
                entry[k_partition_type] = 'NTFS'
            elif 'MSDOS' in type_:
                entry[k_partition_type] = 'FAT32'

        def target():
            partition = get_partition_obj(entry,
                                          self._current_stream)

            self.signal_partition_loaded.emit(partition, row)

        self.do_async_task(target, title_before='正在载入分区...')

    def _set_current_partition(self, partition, row):
        if not partition:
            error_box(self, '你选择了类型未被支持的分区')
            return

        self._current_partition = partition
        self._current_partition_address = (self._stream_type,
                                           self._stream_arg,
                                           row)

    def current_partition(self):
        if not self._current_partition:
            warning_box(self,
                        '请先选择一个分区！')
            return

        return self._current_partition

    def current_partition_address_text(self):
        type_, arg, row = self._current_partition_address
        _1 = ('物理驱动器%s' % arg
              if type_ == WindowsPhysicalDriveStream
              else '镜像文件%s' % arg)

        return '%s上的第%s个分区' % (_1, row)

    def exec_(self, *args, **kwargs):
        self._current_stream = None
        self._current_partition = None
        self._current_partition_address = ''
        self._partition_table = []

        self._load_wpd()

        return super().exec_(*args, **kwargs)
