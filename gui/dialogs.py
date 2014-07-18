# encoding: utf-8
import logging
import os
from PySide.QtCore import *
from PySide.QtGui import *
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg, \
    NavigationToolbar2QTAgg
from drive.boot_sector.misc import supported_partition_types
from drive.keys import k_partition_type, k_OEM_name, k_ignored, \
    k_first_sector_address, k_number_of_sectors, k_bytes_per_sector
from drive.utils import get_partition_table, discover_physical_drives, \
    get_partition_obj
from gui.widgets import ColumnListView
from .misc import LoggerHandler, ColoredFormatter, error_box, AsyncTaskMixin, \
    new_button, warning_box, human_readable
from stream import ImageStream, WindowsPhysicalDriveStream


class SettingsDialog(QDialog):
    def __init__(self, parent):
        super(SettingsDialog, self).__init__(parent)
        self.setModal(False)
        self.setWindowTitle('Settings')

        self.attr_include_deleted_files = False
        self.attr_include_folders = True
        self.attr_sort = False
        self.attr_sort_by = ''
        self.attr_display_entry_log = False
        self.attr_plot_first_cluster = True
        self.attr_plot_avg_cluster = True
        self.attr_window_size = 5
        self.attr_window_step = 1
        self.attr_attr1_expr = '_.create_time.timestamp()'
        self.attr_attr2_expr = '_.first_cluster'

        self.attr_tau = True
        self.attr_tau_format = 'Dx--'
        self.attr_tau_value_domain_min = 0
        self.attr_tau_value_domain_max = 1
        self.attr_tau_value_domain = [self.attr_tau_value_domain_min,
                                      self.attr_tau_value_domain_max]
        self.attr_tau_rect_size_width = 5
        self.attr_tau_rect_size_height = 0.5
        self.attr_tau_rect_size = [self.attr_tau_rect_size_width,
                                   self.attr_tau_rect_size_height]
        self.attr_tau_threshold = 2
        self.attr_tau_plot_normal_points = True
        self.attr_tau_plot_abnormal_points = True

        self.attr_rho = True
        self.attr_rho_format = '^v-'
        self.attr_rho_value_domain_min = -1
        self.attr_rho_value_domain_max = 1
        self.attr_rho_value_domain = [self.attr_rho_value_domain_min,
                                      self.attr_rho_value_domain_max]
        self.attr_rho_rect_size_width = 5
        self.attr_rho_rect_size_height = 0.5
        self.attr_rho_rect_size = [self.attr_rho_rect_size_width,
                                   self.attr_rho_rect_size_height]
        self.attr_rho_threshold = 2
        self.attr_rho_plot_normal_points = True
        self.attr_rho_plot_abnormal_points = True

        self.attr_cluster_plot = True
        self.attr_cluster_plot_format = 'D^--'
        self.attr_cluster_plot_value_domain_min = 2
        self.attr_cluster_plot_value_domain_max = 2 ** 32
        self.attr_cluster_plot_value_domain = [
            self.attr_cluster_plot_value_domain_min,
            self.attr_cluster_plot_value_domain_max
        ]
        self.attr_cluster_plot_rect_size_width = 5
        self.attr_cluster_plot_rect_size_height = 10
        self.attr_cluster_plot_rect = [self.attr_cluster_plot_rect_size_width,
                                       self.attr_cluster_plot_rect_size_height]
        self.attr_cluster_plot_threshold = 2
        self.attr_cluster_plot_plot_normal_points = True
        self.attr_cluster_plot_plot_abnormal_points = True

        self.attr_plot_tau_and_rho_on_the_same_figure = True

        self.setup_layout()

    def setup_layout(self):
        def create_plot_settings_group_box(group_name, group_title,
                                           value_domain_type='float'):
            def attr_name(name):
                return 'attr_%s_%s' % (group_name, name)

            def attr_value(name):
                return getattr(self, attr_name(name))

            def new_line_edit(name,
                              integer=False,
                              float_=False,
                              big_integer=False):
                f = lambda _: _.value()

                if integer:
                    _ = QSpinBox()
                    _.setValue(attr_value(name))
                    _signal = _.valueChanged
                elif float_:
                    _ = QDoubleSpinBox()
                    _.setDecimals(2)
                    _.setSingleStep(0.1)
                    _.setMinimum(-10)
                    _.setValue(attr_value(name))
                    _signal = _.valueChanged
                elif big_integer:
                    _ = QLineEdit(str(attr_value(name)))
                    f = lambda _: int(_.text())
                    _signal = _.editingFinished
                else:
                    _ = QLineEdit(attr_value(name))
                    f = lambda _: _.text()
                    _signal = _.editingFinished

                def _slot():
                    setattr(self, attr_name(name), f(_))
                _signal.connect(_slot)

                return _

            def new_checkbox(title, name):
                _ = QCheckBox(title)
                _.setChecked(attr_value(name))

                def _slot(state):
                    setattr(self, attr_name(name), state == Qt.Checked)
                _.stateChanged.connect(_slot)

                return _

            le_format = new_line_edit('format')
            lb_format = QLabel('格式:')
            lb_format.setBuddy(le_format)

            le_domain_min = new_line_edit(
                'value_domain_min',
                float_=value_domain_type == 'float',
                integer=value_domain_type == 'integer',
                big_integer=value_domain_type == 'big_integer'
            )
            le_domain_max = new_line_edit(
                'value_domain_max',
                float_=value_domain_type == 'float',
                integer=value_domain_type == 'integer',
                big_integer=value_domain_type == 'big_integer'
            )
            lb_domain = QLabel('参数值域:')
            lb_domain.setBuddy(le_domain_min)

            le_rect_size_width = new_line_edit('rect_size_width', integer=True)
            le_rect_size_height = new_line_edit('rect_size_height', float_=True)
            lb_rect_size = QLabel('矩形大小:')
            lb_rect_size.setBuddy(le_rect_size_width)

            le_threshold = new_line_edit('threshold', integer=True)
            lb_threshold = QLabel('阈值:')
            lb_threshold.setBuddy(le_threshold)

            cb_plot_normal = new_checkbox('绘制正常点',
                                          'plot_normal_points')
            cb_plot_abnormal = new_checkbox('绘制异常点',
                                            'plot_abnormal_points')
            hl = QHBoxLayout()
            hl.addWidget(cb_plot_normal)
            hl.addWidget(cb_plot_abnormal)

            grid_layout = QGridLayout()
            grid_layout.addWidget(lb_format, 0, 0, 1, 1)
            grid_layout.addWidget(le_format, 0, 1, 1, 2)
            grid_layout.addWidget(lb_domain, 1, 0, 1, 1)
            grid_layout.addWidget(le_domain_min, 1, 1, 1, 1)
            grid_layout.addWidget(le_domain_max, 1, 2, 1, 1)
            grid_layout.addWidget(lb_rect_size, 2, 0, 1, 1)
            grid_layout.addWidget(le_rect_size_width, 2, 1, 1, 1)
            grid_layout.addWidget(le_rect_size_height, 2, 2, 1, 1)
            grid_layout.addWidget(lb_threshold, 3, 0, 1, 1)
            grid_layout.addWidget(le_threshold, 3, 1, 1, 2)
            grid_layout.addLayout(hl, 4, 0, 1, 3)

            group_box = QGroupBox(group_title)
            group_box.setCheckable(True)
            group_box.setChecked(getattr(self, attr_name('')[:-1]))
            group_box.setLayout(grid_layout)
            group_box.toggled.connect(lambda on: setattr(self,
                                                         attr_name('')[:-1],
                                                         on))

            return group_box

        def attr_name(name):
            return 'attr_%s' % name

        def attr_value(name):
            return getattr(self, attr_name(name))

        def new_checkbox(name, title, slot=None):
            _ = QCheckBox(title)
            _.setChecked(attr_value(name))
            _.stateChanged.connect(
                slot or (lambda state: setattr(self,
                                               attr_name(name),
                                               state == Qt.Checked))
            )

            return _

        def new_line_edit(name, title, integer=True):
            _ = QLineEdit(str(attr_value(name)))

            if integer:
                _.setValidator(QIntValidator())

            _.editingFinished.connect(
                lambda: setattr(self,
                                attr_name(name),
                                (int if integer else str)(_.text()))
            )

            label = QLabel(title)
            label.setBuddy(_)

            return label, _

        hb1 = QHBoxLayout()
        for group_name, group_title, value_domain_type in zip(
                ['tau', 'rho', 'cluster_plot'],
                ['Kendall\'s tau 参数',
                 'Spearman\'s rho 参数',
                 '簇号图'],
                ['float', 'float', 'big_integer']
        ):
            hb1.addWidget(create_plot_settings_group_box(group_name,
                                                         group_title,
                                                         value_domain_type))

        cb_plot_on_same_figure = new_checkbox(
            'plot_tau_and_rho_on_the_same_figure',
            '将tau与rho绘制在同一张图上'
        )

        l_window_size, le_window_size = new_line_edit('window_size',
                                                      '窗口大小:')
        l_window_step, le_window_step = new_line_edit('window_step',
                                      '窗口间隔:')
        l_attr1_expr, le_attr1_expr = new_line_edit('attr1_expr',
                                                    '参数1表达式:',
                                                    integer=False)
        l_attr2_expr, le_attr2_expr = new_line_edit('attr2_expr',
                                                    '参数2表达式:',
                                                    integer=False)

        gl = QGridLayout()
        gl.addWidget(l_window_size, 0, 0, 1, 1)
        gl.addWidget(le_window_size, 0, 1, 1, 1)
        gl.addWidget(l_window_step, 0, 2, 1, 1)
        gl.addWidget(le_window_step, 0, 3, 1, 1)
        gl.addWidget(l_attr1_expr, 1, 0, 1, 1)
        gl.addWidget(le_attr1_expr, 1, 1, 1, 1)
        gl.addWidget(l_attr2_expr, 1, 2, 1, 1)
        gl.addWidget(le_attr2_expr, 1, 3, 1, 1)

        vb = QVBoxLayout()
        vb.addLayout(hb1)
        vb.addWidget(cb_plot_on_same_figure)
        vb.addLayout(gl)

        metrics_plot_settings_group_box = QGroupBox('参数图设置')
        metrics_plot_settings_group_box.setLayout(vb)

        cb_include_deleted_files = new_checkbox('include_deleted_files',
                                                '绘制标记为删除的项目')
        cb_include_folders = new_checkbox('include_folders',
                                          '绘制文件夹项目')

        cb_sort_by = QComboBox()
        cb_sort_by.setEnabled(self.attr_sort)
        cb_sort_by.addItems(['create_time', 'modify_time', 'access_time',
                             'first_cluster', 'FDT顺序'])
        cb_sort_by.currentIndexChanged.connect(
            lambda item: setattr(self,
                                 attr_name('sort_by'),
                                 item if item != 'FDT顺序' else ''))

        def _slot(state):
            self.attr_sort = state == Qt.Checked
            cb_sort_by.setEnabled(self.attr_sort)
        cb_sort = new_checkbox('sort', '排序关键字', _slot)

        l_sort = QHBoxLayout()
        l_sort.addWidget(cb_sort)
        l_sort.addWidget(cb_sort_by)

        cb_display_entry_log = new_checkbox('display_entry_log',
                                            '记录项目日志')

        btn_show_hide_log_dialog = QPushButton('显示/隐藏日志窗口')
        btn_show_hide_log_dialog.clicked.connect(
            lambda: self.parent().log_dialog.hide()
                    if self.parent().log_dialog.isVisible()
                    else self.parent().log_dialog.show()
        )

        cb_plot_first_cluster = new_checkbox('plot_first_cluster',
                                             '绘制首簇图')
        cb_plot_avg_cluster = new_checkbox('plot_avg_cluster',
                                           '绘制平均簇号图')

        vl = QVBoxLayout()
        vl.addWidget(cb_include_deleted_files)
        vl.addWidget(cb_include_folders)
        vl.addLayout(l_sort)
        vl.addWidget(cb_display_entry_log)
        vl.addWidget(btn_show_hide_log_dialog)
        vl.addWidget(cb_plot_first_cluster)
        vl.addWidget(cb_plot_avg_cluster)

        general_plot_settings_group_box = QGroupBox('一般设置')
        general_plot_settings_group_box.setLayout(vl)

        layout = QHBoxLayout()
        layout.addWidget(general_plot_settings_group_box)
        layout.addWidget(metrics_plot_settings_group_box)

        self.setLayout(layout)

    def __getattr__(self, item):
        return self.__getattribute__('attr_%s' % item)


class LogDialog(QDialog):

    signal_new_log = Signal(str)
    colored_formatter = ColoredFormatter(
        fmt='{asctime} - {name} - {levelname}: {message}',
        colors={'asctime': lambda _: 'blue',
                'levelname': lambda lvl:
                    ColoredFormatter.gen_colorscheme()[lvl],
                'name': lambda _: 'gray'},
        datefmt='%m/%dT%H:%M:%S'
    )

    def __init__(self, parent):
        super(LogDialog, self).__init__(parent)
        self.setModal(False)
        self.setWindowTitle('Log')
        self.resize(400, 200)
        self.log_widget = QTextBrowser()

        layout = QVBoxLayout()
        layout.addWidget(self.log_widget)
        self.setLayout(layout)

        self.signal_new_log.connect(self.log_widget.append)

    def new_handler(self):
        handler = LoggerHandler(self)
        handler.setFormatter(self.colored_formatter)

        return handler


class PartitionDialog(QDialog, AsyncTaskMixin):

    signal_partition_read = Signal(int, str, object)
    signal_wpd_loaded = Signal(list)
    signal_partition_loaded = Signal(object, int)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.setup_mixin(kwargs['parent'])

        self.original_title = '选择分区'
        self.setWindowTitle(self.original_title)

        self._lw_wpd = QListWidget()
        self._clv_partitions = ColumnListView(['',
                                               '类型',
                                               '起始扇区',
                                               '大小',
                                               '扇区数'],
                                              self,
                                              headers_fit_content=True)

        self._current_stream = None
        self._partition_table = []
        self._current_partition = None

        self._stream_type, self._stream_arg = '', None

        self._setup_layout()
        self._setup_connections()

        self._load_wpd()

    def _setup_connections(self):
        def _partition_read(i, t, p):
            size = p[k_number_of_sectors] * p.get(k_bytes_per_sector, 512)

            self._clv_partitions.append([i,
                                         t,
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

        if isinstance(entry[k_partition_type], int) and\
           entry[k_partition_type] not in supported_partition_types:
            error_box(self,
                      '不支持所选的分区类型（类型：%s）' %
                      entry[k_partition_type])
            return

        def target():
            self.parent().logger.info(row, entry)
            partition = get_partition_obj(entry,
                                          self._current_stream,
                                          self.parent().log_dialog.new_handler())

            if not self.parent().settings_dialog.display_entry_log:
                partition.logger.setLevel(logging.INFO)
            else:
                partition.logger.setLevel(logging.DEBUG)

            self.signal_partition_loaded.emit(partition, row)

        self.do_async_task(target, title_before='正在载入分区...')

    def _set_current_partition(self, partition, row):
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

    def accept(self, *args, **kwargs):
        return super().accept()


class FigureDialog(QDialog):
    def __init__(self, parent, figure, title='绘图结果'):
        super().__init__(parent=parent)

        self.setWindowTitle(title)

        self.setModal(False)

        self.figure_widget = FigureCanvasQTAgg(figure)
        self.figure_widget.setSizePolicy(QSizePolicy.Expanding,
                                         QSizePolicy.Expanding)
        self.figure_widget.updateGeometry()

        self.navbar = NavigationToolbar2QTAgg(self.figure_widget,
                                              self)

        layout = QVBoxLayout()
        layout.addWidget(self.figure_widget)
        layout.addWidget(self.navbar)
        self.setLayout(layout)
