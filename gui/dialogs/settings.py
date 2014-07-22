# encoding: utf-8
from PySide.QtCore import *
from PySide.QtGui import *

class SettingsDialog(QDialog):
    def __init__(self, parent):
        super(SettingsDialog, self).__init__(parent)
        self.setModal(False)
        self.setWindowTitle('Settings')

        self.attr_include_deleted_files = False
        self.attr_include_folders = True
        self.attr_sort_fat32 = False
        self.attr_sort_fat32_by = ''
        self.attr_sort_ntfs = False
        self.attr_sort_ntfs_by = ''
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

        cb_sort_fat32_by = QComboBox()
        cb_sort_fat32_by.setEnabled(self.attr_sort_fat32)
        cb_sort_fat32_by.addItems(['create_time', 'modify_time', 'access_time',
                             'first_cluster', 'FDT顺序'])
        cb_sort_fat32_by.currentIndexChanged.connect(
            lambda item: setattr(self,
                                 attr_name('sort_fat32_by'),
                                 item if item != 'FDT顺序' else '')
        )

        def _slot(state):
            self.attr_sort_fat32 = state == Qt.Checked
            cb_sort_fat32_by.setEnabled(self.attr_sort_fat32)
        cb_sort_fat32 = new_checkbox('sort_fat32', 'FAT32排序关键字', _slot)

        l_sort_fat32 = QHBoxLayout()
        l_sort_fat32.addWidget(cb_sort_fat32)
        l_sort_fat32.addWidget(cb_sort_fat32_by)

        cb_sort_ntfs_by = QComboBox()
        cb_sort_ntfs_by.setEnabled(self.attr_sort_ntfs)
        cb_sort_ntfs_by.addItems(['日志文件序号', 'si_create_time'])
        cb_sort_ntfs_by.currentIndexChanged.connect(
            lambda item: setattr(self,
                                 attr_name('sort_ntfs_by'),
                                 item if item != '日志文件序号' else '')
        )

        def _slot(state):
            self.attr_sort_ntfs = state == Qt.Checked
            cb_sort_ntfs_by.setEnabled(self.attr_sort_ntfs)
        cb_sort_ntfs = new_checkbox('sort_ntfs', 'NTFS排序关键字', _slot)

        l_sort_ntfs = QHBoxLayout()
        l_sort_ntfs.addWidget(cb_sort_ntfs)
        l_sort_ntfs.addWidget(cb_sort_ntfs_by)

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
        vl.addLayout(l_sort_fat32)
        vl.addLayout(l_sort_ntfs)
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
