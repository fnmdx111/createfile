# encoding: utf-8
import logging
from PySide.QtGui import *
from PySide.QtCore import *
from drive.fs.fat32 import FAT32, plot_fat32
from drive.boot_sector.misc import supported_partition_types
from drive.keys import k_partition_type, k_first_sector_address,\
    k_number_of_sectors, k_ignored, k_OEM_name, k_bytes_per_sector
from drive.utils import discover_physical_drives, get_partition_table, \
    get_partition_obj
from .dialogs import SettingsDialog, LogDialog
from stream import ImageStream, WindowsPhysicalDriveStream


class MainWindow(QMainWindow):

    signal_title_changed = Signal(str)
    signal_title_restored = Signal()
    signal_loaded_windows_physical_drives = Signal(list)
    signal_partition_read = Signal(int, str, object)
    signal_partition_loaded = Signal(object)
    signal_partition_parsed = Signal(object)

    def __init__(self):
        super(MainWindow, self).__init__()

        self.lw_wpd = QListWidget()
        self.tv_partitions = QTreeView()
        self.tv_partitions_model = QStandardItemModel(self)
        self.tv_partitions_selection_model = None
        self.setup_partitions_view()
        self.lv_rules = QListView()

        self.settings_dialog = self.settings = SettingsDialog(self)
        self.log_dialog = LogDialog(self)

        self.setup_layout()
        self.title = 'createfile - Integrated Time Authenticity Analyzer'
        self.setWindowTitle(self.title)

        self.load_windows_physical_drives()

        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(self.log_dialog.handler)

        self.current_stream = None
        self.current_partition = None
        self.partition_table = []

        self.connect_custom_signals()

    def connect_custom_signals(self):
        self.signal_loaded_windows_physical_drives.connect(
            self.fill_in_windows_physical_drives_view
        )
        self.signal_title_changed.connect(self.append_title)
        self.signal_title_restored.connect(self.restore_title)
        self.signal_partition_read.connect(self.append_partition_row)
        self.signal_partition_loaded.connect(self.set_current_partition)
        self.signal_partition_parsed.connect(self.gen_plot_partition_slot())

    def set_current_partition(self, partition):
        self.current_partition = partition

    def append_title(self, title):
        self.setWindowTitle('%s | %s' % (self.windowTitle(), title))

    def restore_title(self):
        self.setWindowTitle(self.title)

    def setup_partitions_view(self):
        self.tv_partitions.setItemsExpandable(False)
        self.tv_partitions.setRootIsDecorated(False)
        self.tv_partitions.header().setResizeMode(QHeaderView.ResizeToContents)

        self.tv_partitions.setModel(self.tv_partitions_model)

        self.tv_partitions.setSelectionMode(QAbstractItemView.SingleSelection)

        self.tv_partitions_selection_model = self.tv_partitions.selectionModel()
        self.tv_partitions_selection_model.currentChanged.connect(
            self.load_partition
        )

        self.setup_partitions_model()

    def setup_partitions_model(self):
        self.tv_partitions_model.setHorizontalHeaderLabels(['',
                                                            'Type',
                                                            'Start sector',
                                                            'Size',
                                                            'Sectors'])

    def load_windows_physical_drives(self):
        self.lw_wpd.clear()

        def _():
            numbers = discover_physical_drives()
            self.signal_loaded_windows_physical_drives.emit(numbers)

        self.do_async_action(_, title_before='loading physical drives...')

    def fill_in_windows_physical_drives_view(self, numbers):
        for n in numbers:
            QListWidgetItem(QFileIconProvider().icon(QFileIconProvider.Drive),
                            r'\\.\PhysicalDrive\%s' % n,
                            self.lw_wpd)

    def setup_layout(self):
        widget = QWidget(self)

        def new_button(text, slot):
            btn = QPushButton(text)
            btn.clicked.connect(slot)

            return btn

        # image path form
        le_image_path = QLineEdit()

        label = QLabel('Image path:')
        label.setBuddy(le_image_path)
        def open_image():
            path, _ = QFileDialog.getOpenFileName(self,
                                                  'Open image file',
                                                  '.',
                                                  'All files (*.*)')
            le_image_path.setText(path if path else le_image_path.text())

        def load_image():
            if not le_image_path.text():
                return

            if self.current_stream:
                self.current_stream.close()

            self.current_stream = ImageStream(le_image_path.text())
            self.load_partitions()

        _l0 = QHBoxLayout()
        _l0.addWidget(label)
        _l0.addWidget(le_image_path)

        _l1 = QHBoxLayout()
        _l1.addWidget(new_button('Open...',
                                 open_image))
        _l1.addWidget(new_button('Load',
                                 load_image))

        _l2 = QVBoxLayout()
        _l2.addLayout(_l0)
        _l2.addLayout(_l1)

        img_group_box = QGroupBox('Using an image')
        img_group_box.setLayout(_l2)

        # list of available windows physical drive
        self.lw_wpd.currentItemChanged.connect(self.wpd_changed)

        _l = QVBoxLayout()
        _l.addWidget(new_button('Refresh', self.load_windows_physical_drives))
        _l.addWidget(self.lw_wpd)

        wpd_group_box = QGroupBox('Using a physical drive')
        wpd_group_box.setLayout(_l)

        # action buttons
        _l = QVBoxLayout()
        _l.addWidget(new_button('Settings...',
                                lambda: self.settings_dialog.show()))
        _l.addWidget(new_button('Plot metrics',
                                self.plot_metrics))
        _l.addWidget(new_button('Plot partition',
                                self.plot_partition))
        _l.addWidget(new_button('Show timeline',
                                self.show_timeline))

        buttons_group_box = QGroupBox('Analysis tools')
        buttons_group_box.setLayout(_l)

        # list of partitions
        _l = QVBoxLayout()
        _l.addWidget(self.tv_partitions)

        partitions_group_box = QGroupBox('Partitions')
        partitions_group_box.setLayout(_l)

        # list of rules
        le_rule = QLineEdit()
        _l = QVBoxLayout()
        _l.addWidget(le_rule)
        _l.addWidget(new_button('Add rule',
                                lambda: None))
        _l.addWidget(self.lv_rules)

        rules_group_box = QGroupBox('Rules to apply')
        rules_group_box.setLayout(_l)

        # setup grid layout
        vertical_line = QFrame(self)
        vertical_line.setFrameShape(QFrame.VLine)
        vertical_line.setFrameShadow(QFrame.Sunken)

        grid_layout = QGridLayout()
        grid_layout.addWidget(buttons_group_box, 0, 0, 1, 1)
        grid_layout.addWidget(rules_group_box, 1, 0, 1, 1)
        grid_layout.addWidget(vertical_line, 0, 1, 2, 1)
        grid_layout.addWidget(img_group_box, 0, 2, 1, 1)
        grid_layout.addWidget(wpd_group_box, 1, 2, 1, 1)
        grid_layout.addWidget(partitions_group_box, 0, 3, 2, 1)

        widget.setLayout(grid_layout)
        self.setCentralWidget(widget)

    def plot_metrics(self):
        pass

    def gen_plot_partition_slot(self):
        def _slot(entries):
            if self.current_partition.type == FAT32.type:
                if not self.settings.include_deleted_files:
                    entries = entries[(entries.is_deleted == False) &
                                      entries.cluster_list]
                if self.settings_dialog.attr_sort:
                    sort_key = self.settings.sort_by
                    if sort_key:
                        entries = entries.sort_index(by=sort_key)

                plot_fat32(
                    entries,
                    log_info=self.settings.display_entry_log,
                    logger=self.logger,
                    plot_first_cluster=self.settings.plot_first_cluster,
                    plot_average_cluster=self.settings.plot_avg_cluster,
                    show=True
                )

        return _slot

    def plot_partition(self):
        if not self.current_partition:
            QMessageBox.warning(self,
                                'Warning',
                                'Please wait till the partition is loaded.',
                                QMessageBox.Ok)
            return

        self.do_async_action(lambda: self.current_partition.get_entries(),
                             signal_after=self.signal_partition_parsed,
                             title_before='parsing partition')

    def show_timeline(self):
        pass

    def wpd_changed(self, current, _):
        if not current:
            return

        if self.current_stream:
            self.current_stream.close()

        self.current_stream = WindowsPhysicalDriveStream(
            current.text().lstrip(r'\\.\PhysicalDrive\ ')
        )

        self.load_partitions()

    @staticmethod
    def non_editable_standard_item(text):
        _ = QStandardItem(text)
        _.setFlags(_.flags() & ~Qt.ItemIsEditable)

        return _

    def load_partitions(self):
        self.partition_table = []

        self.tv_partitions_model.clear()
        self.setup_partitions_model()

        def _():
            for i, p in enumerate(get_partition_table(self.current_stream)):
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

        self.do_async_action(_, title_before='loading partition table...')

    def append_partition_row(self, i, type_, p):
        self.partition_table.append(p)

        size = p[k_number_of_sectors] * p.get(k_bytes_per_sector, 512)

        self.tv_partitions_model.appendRow(
            [self.non_editable_standard_item(str(i)),
             self.non_editable_standard_item(type_),
             self.non_editable_standard_item(
                 str(p.get(k_first_sector_address, 0))
             ),
             self.non_editable_standard_item(self.to_human_readable(size)),
             self.non_editable_standard_item(str(p[k_number_of_sectors]))]
        )

    def load_partition(self, current_idx, _):
        row = current_idx.row()
        if not -1 < row < len(self.partition_table):
            QMessageBox.warning(self,
                                'Warning',
                                'No valid partition selected.',
                                QMessageBox.Ok)
            return

        entry = self.partition_table[self.tv_partitions.currentIndex().row()]

        if isinstance(entry[k_partition_type], int) and\
           entry[k_partition_type] not in supported_partition_types:
            QMessageBox.critical(self,
                                 'Error',
                                 'Selected partition (partition type %s) is '
                                 'not supported.' % entry[k_partition_type],
                                 QMessageBox.Ok)
            return

        def target():
            partition = get_partition_obj(entry,
                                          self.current_stream,
                                          self.log_dialog.handler)

            if not self.settings_dialog.attr_display_entry_log:
                partition.logger.setLevel(logging.INFO)
            else:
                partition.logger.setLevel(logging.DEBUG)

            self.signal_partition_loaded.emit(partition)

        self.do_async_action(target, title_before='loading partition...')

    A_MILLION_BYTE = 1024 * 1024
    def to_human_readable(self, size):
        size_f = float(size)
        if size > 1024 * 1024 * 1024:
            human_readable_size = '%.2f GB' % (size_f /
                                                  (self.A_MILLION_BYTE * 1024))
        elif size > 1024 * 1024:
            human_readable_size = '%.2f MB' % (size_f / self.A_MILLION_BYTE)
        elif size > 1024:
            human_readable_size = '%.2f KB' % (size_f / 1024)
        else:
            human_readable_size = '%.2f B' % size_f
        return human_readable_size

    class DummyThread(QThread):
        def __init__(self, target, parent):
            super().__init__(parent)
            self.target = target

        def run(self):
            self.target()

    def do_async_action(self, target,
                        signal_before=None, signal_after=None,
                        title_before='', title_after=''):
        def _():
            if title_before:
                self.signal_title_changed.emit(title_before)

            if signal_before:
                signal_before.emit()

            ret = target()

            if signal_after:
                signal_after.emit(ret)

            self.signal_title_restored.emit()

            if title_after:
                self.signal_title_changed.emit(title_after)

        thread = self.DummyThread(_, self)
        thread.start()
