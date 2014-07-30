# encoding: utf-8
from collections import OrderedDict
from itertools import product

from PySide.QtGui import *
from PySide.QtCore import *


class MetricsSettingsWidget(QWidget):

    __attr__ = ['format',
                'value_domain_min', 'value_domain_max',
                'rect_size_width', 'rect_size_height',
                'window_size', 'window_step',
                'threshold',
                'plot_normal_points', 'plot_abnormal_points']

    def __init__(self, parent, method, title, defaults, statistical,
                 value_domain_types=('float', 'float')):
        super().__init__(parent=parent)

        setattr(self, method, True)

        def _(name):
            return '%s_%s' % (method, name)

        self.method = method
        self.value_domain_types = value_domain_types
        self.statistical = statistical

        self.attrs = self.__attr__ + (['attr1', 'attr2'] if statistical else [])

        for attr in self.attrs:
            setattr(self, _(attr), defaults[attr])

        self.setup_layout(title)

    def export(self):
        values = [self.method]
        for attr in self.attrs:
            values.append(getattr(self, attr))

        return values

    def import_(self, values):
        def an(name):
            return '%s_%s' % (self.method, name)

        if values[0] != self.method:
            return

        self.group_box.setChecked(True)
        for attr, value in zip(self.attrs, values[1:]):
            setattr(self, an(attr), value)
            if isinstance(value, bool):
                getattr(self, 'cb_%s' % an(attr)).setCheckState(
                    Qt.Checked if value else Qt.Unchecked
                )
            elif isinstance(value, float):
                getattr(self, 'le_%s' % an(attr)).setValue(value)
            elif isinstance(value, int):
                getattr(self, 'le_%s' % an(attr)).setValue(value)
            else:
                getattr(self, 'le_%s' % an(attr)).setText(str(value))

    def setup_layout(self, title):
        def an(name):
            return '%s_%s' % (self.method, name)

        def av(name):
            return getattr(self, an(name))

        def new_line_edit(name, integer=False, float_=False, big_integer=False):
            f = lambda _: _.value()

            if integer:
                _ = QSpinBox()
                _.setValue(av(name))
                _signal = _.valueChanged
            elif float_:
                _ = QDoubleSpinBox()
                _.setDecimals(2)
                _.setSingleStep(0.1)
                _.setMinimum(-10)
                _.setValue(av(name))
                _signal = _.valueChanged
            elif big_integer:
                _ = QLineEdit(str(av(name)))
                f = lambda _: int(_.text())
                _signal = _.editingFinished
            else:
                _ = QLineEdit(av(name))
                f = lambda _: _.text()
                _signal = _.editingFinished

            def _slot():
                setattr(self, an(name), f(_))
            _signal.connect(_slot)

            setattr(self, 'le_%s' % name, _)

            return _

        def new_checkbox(title, name):
            _ = QCheckBox(title)
            _.setChecked(av(name))

            def _slot(state):
                setattr(self, an(name), state == Qt.Checked)
            _.stateChanged.connect(_slot)

            setattr(self, 'cb_%s' % name, _)

            return _

        le_format = new_line_edit('format')
        lb_format = QLabel('格式:')
        lb_format.setBuddy(le_format)

        le_domain_min = new_line_edit(
            'value_domain_min',
            float_=self.value_domain_types[0] == 'float',
            integer=self.value_domain_types[0] == 'integer',
            big_integer=self.value_domain_types[0] == 'big_integer'
        )
        le_domain_max = new_line_edit(
            'value_domain_max',
            float_=self.value_domain_types[0] == 'float',
            integer=self.value_domain_types[0] == 'integer',
            big_integer=self.value_domain_types[0] == 'big_integer'
        )
        lb_domain = QLabel('参数值域:')
        lb_domain.setBuddy(le_domain_min)

        le_rect_size_width = new_line_edit('rect_size_width', integer=True)
        le_rect_size_height = new_line_edit(
            'rect_size_height',
            float_=self.value_domain_types[1] == 'float',
            integer=self.value_domain_types[1] == 'integer',
            big_integer=self.value_domain_types[1] == 'big_integer'
        )
        lb_rect_size = QLabel('矩形大小:')
        lb_rect_size.setBuddy(le_rect_size_width)

        le_window_size = new_line_edit('window_size', integer=True)
        lb_window_size = QLabel('窗口大小:')
        lb_window_size.setBuddy(le_window_size)

        le_window_step = new_line_edit('window_step', integer=True)
        lb_window_step = QLabel('窗口步长:')
        lb_window_step.setBuddy(le_window_step)

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
        grid_layout.addWidget(lb_format, 0, 0)
        grid_layout.addWidget(le_format, 0, 1, 1, 2)
        grid_layout.addWidget(lb_domain, 1, 0)
        grid_layout.addWidget(le_domain_min, 1, 1)
        grid_layout.addWidget(le_domain_max, 1, 2)
        grid_layout.addWidget(lb_rect_size, 2, 0)
        grid_layout.addWidget(le_rect_size_width, 2, 1)
        grid_layout.addWidget(le_rect_size_height, 2, 2)
        grid_layout.addWidget(lb_threshold, 3, 0)
        grid_layout.addWidget(le_threshold, 3, 1, 1, 2)
        grid_layout.addWidget(lb_window_size, 4, 0)
        grid_layout.addWidget(le_window_size, 4, 1, 1, 2)
        grid_layout.addWidget(lb_window_step, 5, 0)
        grid_layout.addWidget(le_window_step, 5, 1, 1, 2)
        grid_layout.addLayout(hl, 6, 0, 1, 3)

        if self.statistical:
            le_attr1 = new_line_edit('attr1')
            lb_attr1 = QLabel('参数表达式1:')
            lb_attr1.setBuddy(le_attr1)

            le_attr2 = new_line_edit('attr2')
            lb_attr2 = QLabel('参数表达式2:')
            lb_attr2.setBuddy(le_attr2)

            grid_layout.addWidget(lb_attr1, 7, 0)
            grid_layout.addWidget(le_attr1, 7, 1, 1, 2)
            grid_layout.addWidget(lb_attr2, 8, 0)
            grid_layout.addWidget(le_attr2, 8, 1, 1, 2)

        group_box = QGroupBox(title)
        group_box.setCheckable(True)
        group_box.setChecked(getattr(self, self.method))
        group_box.setLayout(grid_layout)
        group_box.toggled.connect(lambda on: setattr(self, self.method, on))

        self.group_box = group_box

        _ = QVBoxLayout()
        _.addWidget(group_box)

        self.setLayout(_)


class BaseSettingsWidget(QWidget):

    PARTITION_PREFIX = '/'
    SYSTEM_ENTRY_NAMES = ['$recycle', 'System Information Volume',
                          '$MFT', '$MFTMirr', '$LogFile', '$Volume',
                          '$AttrDef', '$Root', '$Bitmap', '$Boot',
                          '$BadClus', '$Quota', '$Secure', '$UpCase',
                          '$Extend'] # etc. ...

    def __init__(self, parent, sort_keys):
        super().__init__(parent=parent)

        self._real_parent = parent

        self.exclude_deleted_files = True
        self.exclude_folders = False
        self.exclude_system_entries = True

        self.sort_keys = sort_keys
        self.sort_by = list(sort_keys.values())[0]

        self.setup_layout()

    def setup_layout(self):
        keys = list(self.sort_keys.keys())

        def _slot(item):
            self.sort_by = self.sort_keys[keys[item]]

        sort_by = QComboBox(self)
        sort_by.addItems(keys)
        sort_by.currentIndexChanged.connect(_slot)
        lb_sort_by = QLabel('文件项排序关键字')
        _ = QHBoxLayout()
        _.addWidget(lb_sort_by)
        _.addWidget(sort_by)

        layout = QVBoxLayout()
        layout.addLayout(_)
        layout.addWidget(self.new_checkbox('排除已删除的文件项',
                                           'exclude_deleted_files'))
        layout.addWidget(self.new_checkbox('排除标记为文件夹的目录项',
                                           'exclude_folders'))
        layout.addWidget(self.new_checkbox('排除系统目录项',
                                           'exclude_system_entries'))

        self.setup_custom_layout(layout)

        btn_reload = QPushButton('应用设置并重新载入分区')
        btn_reload.clicked.connect(self._real_parent.reload)

        layout.addWidget(btn_reload)

        self.setLayout(layout)

    def new_checkbox(self, title, name):
        _ = QCheckBox(title)
        _.setChecked(getattr(self, name))

        def _slot(state):
            setattr(self, name, state == Qt.Checked)
        _.stateChanged.connect(_slot)

        setattr(self, 'cb_%s' % name, _)

        return _

    def export(self):
        return {'exclude_deleted_files': self.exclude_deleted_files,
                'exclude_folders': self.exclude_folders,
                'exclude_system_entries': self.exclude_system_entries}

    def import_(self, parameters):
        for k, v in parameters.items():
            if hasattr(self, k):
                setattr(self, k, v)
                getattr(self, 'cb_%s' % k).setCheckState(
                    Qt.Checked if v else Qt.Unchecked
                )

    def setup_custom_layout(self, layout):
        raise NotImplementedError

    def filter(self, entries):
        if self.exclude_deleted_files:
            entries = entries[entries.is_deleted == False]
        if self.exclude_folders:
            entries = entries[entries.is_directory == False]
        if self.exclude_system_entries:
            for system_entry_name in self.SYSTEM_ENTRY_NAMES:
                entries = entries[~entries.full_path.str.startswith(
                    '%s%s' % (self.PARTITION_PREFIX, system_entry_name)
                )]

        return entries

    def sort(self, entries):
        return entries.sort(columns=[self.sort_by])


class FAT32SettingsWidget(BaseSettingsWidget):
    def __init__(self, parent):
        self.plot_first_cluster = True
        self.plot_avg_cluster = True
        self.enable_metrics_abnormality_detection = False

        self.start_time_attr = 'create_time'

        super().__init__(parent=parent,
                         sort_keys=OrderedDict([('创建时间', 'create_time'),
                                                ('修改时间', 'modify_time'),
                                                ('访问日期', 'access_date'),
                                                ('首簇号', 'first_cluster'),
                                                ('FDT顺序', 'id')]))

    def setup_custom_layout(self, layout):
        layout.addWidget(self.new_checkbox('绘制首簇折线',
                                           'plot_first_cluster'))
        layout.addWidget(self.new_checkbox('绘制平均簇号折线',
                                           'plot_avg_cluster'))
        layout.addWidget(self.new_checkbox(
            '启用参数异常报警',
            'enable_metrics_abnormality_detection')
        )

        self.tau_settings = MetricsSettingsWidget(
            self, 'tau', "Kendall's tau",
            {'format': 'Dx--',
             'value_domain_min': 0,
             'value_domain_max': 1,
             'rect_size_width': 5,
             'rect_size_height': 0.5,
             'window_size': 5,
             'window_step': 1,
             'threshold': 2,
             'plot_normal_points': True,
             'plot_abnormal_points': True,
             'attr1': '_.create_time.timestamp()',
             'attr2': '_.first_cluster'},
            statistical=True)

        self.rho_settings = MetricsSettingsWidget(
            self, 'rho', "Spearman's rho",
            {'format': '^v-',
             'value_domain_min': -1,
             'value_domain_max': 1,
             'rect_size_width': 5,
             'rect_size_height': 0.5,
             'window_size': 5,
             'window_step': 1,
             'threshold': 2,
             'plot_normal_points': True,
             'plot_abnormal_points': True,
             'attr1': '_.create_time.timestamp()',
             'attr2': '_.first_cluster'},
            statistical=True)

        self.cluster_plot_settings = MetricsSettingsWidget(
            self, 'cluster_plot', "簇号",
            {'format': 'D^--',
             'value_domain_min': 2,
             'value_domain_max': 2 ** 32,
             'rect_size_width': 5,
             'rect_size_height': 10,
             'window_size': 5,
             'window_step': 1,
             'threshold': 2,
             'plot_normal_points': True,
             'plot_abnormal_points': True},
            statistical=False,
            value_domain_types=('big_integer', 'big_integer'))

        metrics_layout = QHBoxLayout()
        metrics_layout.addWidget(self.tau_settings)
        metrics_layout.addWidget(self.rho_settings)
        metrics_layout.addWidget(self.cluster_plot_settings)
        metrics_settings = QDialog(self)
        metrics_settings.setLayout(metrics_layout)

        btn = QPushButton('参数图选项...')
        btn.clicked.connect(metrics_settings.show)
        layout.addWidget(btn)

    def export(self):
        my = {'plot_first_cluster': self.plot_first_cluster,
              'plot_avg_cluster': self.plot_avg_cluster,
              'enable_metrics_abnormality_detection':
                  self.enable_metrics_abnormality_detection,
              'tau': self.tau_settings.export(),
              'rho': self.rho_settings.export(),
              'cluster_plot': self.cluster_plot_settings.export()}
        my.update(super().export())

        return my

    def import_(self, parameters):
        super().import_(parameters)

        for k, v in parameters.items():
            if k in ['tau', 'rho', 'cluster_plot']:
                getattr(self, '%s_settings' % k).import_(v)

    def filter(self, entries):
        entries = super().filter(entries)

        return entries

    def __getattr__(self, item):
        obj = None
        if item.startswith('cluster_plot'):
            obj = self.cluster_plot_settings
        elif item.startswith('tau'):
            obj = self.tau_settings
        elif item.startswith('rho'):
            obj = self.rho_settings

        if obj:
            return getattr(obj, item)
        else:
            return None


class NTFSSettingsWidget(BaseSettingsWidget):

    __sort_keys__ = []
    for (ctg_name, ctg), (attr_name, attr) in product(zip(['$SI', '$FN'],
                                                          ['si', 'fn']),
                                                      zip(['创建时间',
                                                           '修改时间',
                                                           '访问时间',
                                                           'MFT修改时间'],
                                                          ['create_time',
                                                           'modify_time',
                                                           'access_time',
                                                           'mft_time'])):
        __sort_keys__.append(('%s%s' % (ctg_name, attr_name),
                              '%s_%s' % (ctg, attr)))
    __sort_keys__.append(('MFT序号', 'id'))

    def __init__(self, parent):
        super().__init__(parent=parent,
                         sort_keys=OrderedDict(NTFSSettingsWidget.__sort_keys__))

    def setup_custom_layout(self, layout):
        pass
