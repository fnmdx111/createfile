# encoding: utf-8
import logging
from PySide.QtCore import *
from PySide.QtGui import *
from .misc import LoggerHandler, ColoredFormatter


class SettingsDialog(QDialog):
    def __init__(self, parent):
        super(SettingsDialog, self).__init__(parent)
        self.setModal(False)
        self.setWindowTitle('Settings')

        self.attr_include_deleted_files = False
        self.attr_sort = False
        self.attr_sort_by = ''
        self.attr_display_entry_log = False
        self.attr_plot_first_cluster = True
        self.attr_plot_avg_cluster = True
        self.attr_window_size = 5
        self.attr_window_step = 1

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
            lb_format = QLabel('Format:')
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
            lb_domain = QLabel('Value domain:')
            lb_domain.setBuddy(le_domain_min)

            le_rect_size_width = new_line_edit('rect_size_width', integer=True)
            le_rect_size_height = new_line_edit('rect_size_height', float_=True)
            lb_rect_size = QLabel('Rect size:')
            lb_rect_size.setBuddy(le_rect_size_width)

            le_threshold = new_line_edit('threshold', integer=True)
            lb_threshold = QLabel('Threshold:')
            lb_threshold.setBuddy(le_threshold)

            cb_plot_normal = new_checkbox('Plot normal points',
                                          'plot_normal_points')
            cb_plot_abnormal = new_checkbox('Plot abnormal points',
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

        def new_line_edit_with_layout(name, title):
            _ = QLineEdit(str(attr_value(name)))
            _.setValidator(QIntValidator())
            _.editingFinished.connect(lambda: setattr(self,
                                                      attr_name(name),
                                                      int(_.text())))

            label = QLabel(title)
            label.setBuddy(_)

            l = QHBoxLayout()
            l.addWidget(label)
            l.addWidget(_)

            return l

        hb1 = QHBoxLayout()
        for group_name, group_title, value_domain_type in zip(
                ['tau', 'rho', 'cluster_plot'],
                ['Kendall\'s tau score',
                 'Spearman\'s rho score',
                 'Cluster number'],
                ['float', 'float', 'big_integer']
        ):
            hb1.addWidget(create_plot_settings_group_box(group_name,
                                                         group_title,
                                                         value_domain_type))

        cb_plot_on_same_figure = new_checkbox(
            'plot_tau_and_rho_on_the_same_figure',
            'Plot tau and rho on the same figure'
        )

        l_window_size = new_line_edit_with_layout('window_size',
                                                  'Window size:')
        l_window_step = new_line_edit_with_layout('window_step',
                                                  'Window step:')

        hb2 = QHBoxLayout()
        hb2.addWidget(cb_plot_on_same_figure)
        hb2.addStretch()
        hb2.addLayout(l_window_size)
        hb2.addStretch()
        hb2.addLayout(l_window_step)

        vb = QVBoxLayout()
        vb.addLayout(hb1)
        vb.addLayout(hb2)

        metrics_plot_settings_group_box = QGroupBox('Metrics plot settings')
        metrics_plot_settings_group_box.setLayout(vb)


        cb_include_deleted_files = new_checkbox('include_deleted_files',
                                                'Include deleted files')

        cb_sort_by = QComboBox()
        cb_sort_by.setEnabled(self.attr_sort)
        cb_sort_by.addItems(['create_time', 'modify_time', 'access_time',
                             'first_cluster', 'FDT order'])
        cb_sort_by.currentIndexChanged.connect(
            lambda item: setattr(self,
                                 attr_name('sort_by'),
                                 item if item != 'FDT order' else ''))

        def _slot(state):
            self.attr_sort = state == Qt.Checked
            cb_sort_by.setEnabled(self.attr_sort)
        cb_sort = new_checkbox('sort', 'Sort by', _slot)

        l_sort = QHBoxLayout()
        l_sort.addWidget(cb_sort)
        l_sort.addWidget(cb_sort_by)

        cb_display_entry_log = new_checkbox('display_entry_log',
                                            'Display entry log')

        btn_show_hide_log_dialog = QPushButton('Show/hide log dialog')
        btn_show_hide_log_dialog.clicked.connect(
            lambda: self.parent().log_dialog.hide()
                    if self.parent().log_dialog.isVisible()
                    else self.parent().log_dialog.show()
        )

        cb_plot_first_cluster = new_checkbox('plot_first_cluster',
                                             'Plot first cluster')
        cb_plot_avg_cluster = new_checkbox('plot_avg_cluster',
                                           'Plot average cluster')

        vl = QVBoxLayout()
        vl.addWidget(cb_include_deleted_files)
        vl.addLayout(l_sort)
        vl.addWidget(cb_display_entry_log)
        vl.addWidget(btn_show_hide_log_dialog)
        vl.addWidget(cb_plot_first_cluster)
        vl.addWidget(cb_plot_avg_cluster)

        general_plot_settings_group_box = QGroupBox('General plot settings')
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

        self.handler = LoggerHandler(self)
        self.handler.setFormatter(self.colored_formatter)
