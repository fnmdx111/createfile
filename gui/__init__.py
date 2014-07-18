# encoding: utf-8
import logging
import os
import webbrowser
from PySide.QtGui import *
from PySide.QtCore import *
from PySide.QtNetwork import QNetworkAccessManager
from PySide.QtWebKit import QWebView
from jinja2 import Environment, PackageLoader
from drive.fs.fat32 import plot_fat32, first_clusters_of_fat32, \
    last_clusters_of_fat32, FAT32
from .dialogs import SettingsDialog, LogDialog, PartitionDialog, FigureDialog
from gui.misc import AsyncTaskMixin, human_readable, new_button
from gui.widgets import RulesWidget, ColumnListView
from stats import calc_windowed_metrics, validate_metrics, plot_windowed_metrics
from stats.speedup.alg import u_tau, u_rho
from stats.validate import validate_clusters


class MainWindow(QMainWindow, AsyncTaskMixin):

    signal_partition_parsed = Signal(object)
    signal_append_to_files_dialog = Signal(object)

    USE_QT_WEBKIT = False

    def __init__(self):
        super().__init__(parent=None)

        self.setup_mixin(self)
        self.partition_dialog = PartitionDialog(parent=self)
        self.settings_dialog = self.settings = SettingsDialog(self)
        self.log_dialog = LogDialog(self)
        self.rw_rules = RulesWidget(self)
        self.clv_files = ColumnListView(['', '路径'],
                                        self)

        self.files_dialog = QDialog(self)
        self.files_dialog.setWindowTitle('文件列表')
        self.files_dialog.setModal(False)

        self.timeline_dialog = QDialog(self)
        self.timeline_dialog.setWindowTitle('时间线')
        self.timeline_dialog.setModal(False)
        self.timeline_view = QWebView(self.timeline_dialog)
        layout = QVBoxLayout()
        layout.addWidget(self.timeline_view)
        self.timeline_dialog.setLayout(layout)

        self.template_path = os.path.join(os.getcwd(), 'gui', 'templates')
        self.timeline_base_url = QUrl.fromLocalFile(self.template_path)

        self.setup_layout()
        self.original_title = ('createfile '
                               ' - Integrated Time Authenticity Analyzer')
        self.setWindowTitle(self.original_title)

        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(self.log_dialog.new_handler())
        self.logger.info('logger ready')

        self.connect_custom_signals()

        self.already_plotted = set()
        self.plotting_schedule = set()
        self.metrics_figures = []
        self.filtered_entries = None
        self.partition_entries = None

        jinja_env = Environment(loader=PackageLoader('gui'))
        self.timeline_template = jinja_env.get_template('timeline.html')

    def connect_custom_signals(self):
        self.signal_metrics_calculation_done.connect(self.check_plotting_status)
        self.signal_append_to_files_dialog.connect(self.clv_files.append)

    def check_plotting_status(self, args):
        self.metrics_figures.append(plot_windowed_metrics(*args, show=False))

        fn = args[3]
        if len(fn) > 1:
            self.already_plotted.add(tuple(fn))
        else:
            self.already_plotted.add(fn[0])

        if self.already_plotted == self.plotting_schedule:
            for figure in self.metrics_figures:
                FigureDialog(self, figure).show()

    def setup_layout(self):
        widget = QWidget(self)

        select_partition_label = '选择分区...'
        btn_select = QPushButton(select_partition_label)
        def select_partition():
            accepted = self.partition_dialog.exec_()
            if accepted:
                btn_select.setText('已选择%s' %
                    self.partition_dialog.current_partition_address_text()
                )
                self.filtered_entries = None
            else:
                btn_select.setText(select_partition_label)
        btn_select.clicked.connect(select_partition)

        # action buttons
        _l = QVBoxLayout()
        _l.addWidget(btn_select)
        _l.addWidget(new_button('设置...',
                                lambda: self.settings_dialog.show()))
        _l.addWidget(new_button('绘制参数图',
                                self.plot_metrics))
        _l.addWidget(new_button('绘制时簇图',
                                self.plot_partition))
        _l.addWidget(new_button('显示时间线',
                                self.show_timeline))

        buttons_group_box = QGroupBox('分析工具箱')
        buttons_group_box.setLayout(_l)

        _l = QVBoxLayout()
        _l.addWidget(self.rw_rules)

        rules_group_box = QGroupBox('规则定义')
        rules_group_box.setLayout(_l)

        layout = QVBoxLayout()
        layout.addWidget(buttons_group_box)
        layout.addWidget(rules_group_box)

        _l = QVBoxLayout()
        _l.addWidget(self.clv_files)
        self.files_dialog.setLayout(_l)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    signal_metrics_calculation_done = Signal(list)
    def plot_metrics(self):
        self.already_plotted = set()
        self.metrics_figures = []

        def _slot(entries):
            funcs = []
            value_domains = []
            rect_sizes = []
            thresholds = []

            func_names = []
            formats = []
            plot_normal = []
            plot_abnormal = []

            for name in ['tau', 'rho']:
                def attr(attr_name=''):
                    return getattr(self.settings,
                                   'attr_%s%s%s' % (name,
                                                    '_' if attr_name else '',
                                                    attr_name))
                if not attr():
                    continue

                if name == 'tau':
                    funcs.append(u_tau)
                elif name == 'rho':
                    funcs.append(u_rho)

                value_domains.append([attr('value_domain_min'),
                                      attr('value_domain_max')])
                rect_sizes.append([attr('rect_size_width'),
                                   attr('rect_size_height')])
                thresholds.append(attr('threshold'))

                func_names.append(name)
                formats.append(attr('format'))
                plot_normal.append(attr('plot_normal_points'))
                plot_abnormal.append(attr('plot_abnormal_points'))

            def do_plot(validator, metrics_func,
                        vd, rs, t,
                        fn, fmt, pn, pa):
                def _():
                    n, a, l = validator(metrics_func(),
                                        vd, rs, t)
                    return n, a, l, fn, fmt, pn, pa
                self.do_async_task(
                    _,
                    title_before='calculating metrics',
                    signal_after=self.signal_metrics_calculation_done
                )

            self.plotting_schedule = set()
            if self.settings.plot_tau_and_rho_on_the_same_figure:
                if self.settings.tau and self.settings.rho:
                    self.plotting_schedule = {('tau', 'rho')}
                else:
                    if self.settings.tau:
                        self.plotting_schedule.add('tau')
                    if self.settings.rho:
                        self.plotting_schedule.add('rho')
            else:
                if self.settings.tau:
                    self.plotting_schedule.add('tau')
                if self.settings.rho:
                    self.plotting_schedule.add('rho')
            if self.settings.cluster_plot:
                self.plotting_schedule.add('first_cluster')

            filtered_entries = self.filter_entries(entries)
            if self.settings.plot_tau_and_rho_on_the_same_figure:
                do_plot(validate_metrics,
                        lambda: calc_windowed_metrics(
                            funcs,
                            filtered_entries,
                            echo=self.settings.display_entry_log,
                            logger=self.logger
                        ),
                        value_domains, rect_sizes, thresholds,
                        func_names, formats, plot_normal, plot_abnormal)
            else:
                for f, vd, rs, t, fn, fmt, pn, pa in zip(funcs,
                                                         value_domains,
                                                         rect_sizes,
                                                         thresholds,
                                                         func_names,
                                                         formats,
                                                         plot_normal,
                                                         plot_abnormal):
                    do_plot(validate_metrics,
                            lambda: calc_windowed_metrics(
                                [f],
                                filtered_entries,
                                echo=self.settings.display_entry_log,
                                logger=self.logger
                            ),
                            [vd], [rs], [t],
                            [fn], [fmt], [pn], [pa])

            if self.settings.cluster_plot:
                do_plot(validate_clusters,
                        lambda: [list(zip(
                            first_clusters_of_fat32(filtered_entries),
                            last_clusters_of_fat32(filtered_entries)
                        ))],
                        [[self.settings.cluster_plot_value_domain_min,
                          self.settings.cluster_plot_value_domain_max]],
                        [[self.settings.cluster_plot_rect_size_width,
                          self.settings.cluster_plot_rect_size_height]],
                        [self.settings.cluster_plot_threshold],
                        ['first_cluster'],
                        [self.settings.cluster_plot_format],
                        [self.settings.cluster_plot_plot_normal_points],
                        [self.settings.cluster_plot_plot_abnormal_points]
                )

        self.parse_partition(_slot)

    def filter_entries(self, entries=None):
        if entries is None:
            if self.filtered_entries is not None:
                return self.filtered_entries
            else:
                return None

        if not self.settings.include_deleted_files:
            entries = entries[(entries.is_deleted == False) &
                              entries.cluster_list]
        if not self.settings.include_folders:
            entries = entries[entries.is_directory == False]
        if self.settings_dialog.attr_sort:
            sort_key = self.settings.sort_by
            if sort_key:
                entries = entries.sort_index(by=sort_key)
        self.filtered_entries = entries

        return entries

    def plot_partition(self):
        def _slot(entries):
            figure = plot_fat32(
                self.filter_entries(entries),
                log_info=self.settings.display_entry_log,
                logger=self.logger,
                plot_first_cluster=self.settings.plot_first_cluster,
                plot_average_cluster=self.settings.plot_avg_cluster,
                show=False
            )
            FigureDialog(self, figure, '时簇图').show()

        self.parse_partition(_slot)

    def parse_partition(self, slot,
                        additional_header=None,
                        additional_info=lambda *_: []):
        # remember to disconnect this signal in your slot
        partition = self.partition_dialog.current_partition()
        if not partition:
            return

        e = self.filter_entries()
        if e is not None:
            slot(e)
            self.files_dialog.show()

            return

        def _slot(entries):
            self.partition_entries = entries

            slot(entries)

            self.clv_files.clear()
            if partition.type == FAT32.type:
                self.clv_files.setup_headers(['',
                                              '路径',
                                              '首簇',
                                              '创建时间',
                                              '修改时间'] +
                                             (additional_header or []))
            for i, (ts, row) in enumerate(
                    self.filter_entries(entries).iterrows()
            ):
                if partition.type == FAT32.type:
                    self.signal_append_to_files_dialog.emit(
                        [i,
                         row.full_path,
                         row.cluster_list[0][0],
                         row.create_time,
                         row.modify_time] + additional_info(i, row)
                    )

            self.files_dialog.show()

            self.signal_partition_parsed.disconnect(_slot)

        self.signal_partition_parsed.connect(_slot)
        self.do_async_task(lambda: partition.get_entries(),
                           signal_after=self.signal_partition_parsed,
                           title_before='正在读取分区...')

    def apply_rules(self, entries):
        result = []
        conclusions = []
        for rule in self.rw_rules.rules():
            conclusions.append(rule.conclusion)

            self.logger.info('applying rule %s to all the entries' %
                             rule.predicate.expr)
            _result, positives = rule.apply_to(self.filter_entries(entries))

            if result:
                for _1, _2 in zip(result, _result):
                    _1.merge(_2)
            else:
                result = _result

        return conclusions, result

    def show_timeline(self):
        result = []
        def _slot(entries):
            conclusions, _result = self.apply_rules(entries)
            result.extend(_result)

            conclusions.append('无可用结论')

            groups, c_id = [], {}
            for i, c in enumerate(conclusions):
                groups.append({'id': i, 'content': c})
                c_id[c]  = i

            items = []
            for i, item in enumerate(_result):
                if item.conclusions:
                    for c in item.conclusions:
                        items.append({
                            'start': item.entry.create_time.timestamp() * 1000,
                            'content': '文件编号%s' % i,
                            'group': c_id[c]
                        })
                else:
                    items.append({
                        'start': item.entry.create_time.timestamp() * 1000,
                        'content': '文件编号%s' % i,
                        'group': len(conclusions) - 1
                    })

            html = self.timeline_template.render(groups=groups,
                                                 items=items)

            if self.USE_QT_WEBKIT:
                self.timeline_view.setHtml(html,
                                           self.timeline_base_url)
                self.timeline_dialog.show()
            else:
                path = os.path.join(self.template_path, 'r.html')
                print(html, file=open(path, 'w', encoding='utf-8'))
                webbrowser.open(QUrl.fromLocalFile(path).toString())

        def _ai(i, _):
            if result:
                _ = result[i]
                return [_.conclusions]

        self.parse_partition(_slot,
                             additional_header=['结论'],
                             additional_info=_ai)
