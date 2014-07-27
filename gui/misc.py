# encoding: utf-8
from datetime import datetime
from logging import Handler, Formatter, makeLogRecord
import threading
from PySide.QtCore import *
from PySide.QtGui import *


class ColoredFormatter(Formatter):
    @staticmethod
    def gen_colorscheme(**kwargs):
        _dict = {'DEBUG': 'gray',
                 'INFO': 'green',
                 'WARNING': 'orange',
                 'ERROR': 'red',
                 'CRITICAL': 'red'}
        for levelname in kwargs:
            _dict[levelname] = kwargs[levelname]

        return _dict

    def __init__(self, fmt=None, datefmt=None, colors=None):
        super(ColoredFormatter, self).__init__(fmt, datefmt)
        if not colors:
            self.colors = {}
        else:
            self.colors = colors

    def format(self, record):
        r = makeLogRecord(record.__dict__)
        for item in self.colors:
            if item == 'asctime':
                info = self.formatTime(r, self.datefmt)
            else:
                info = getattr(r, item)
            setattr(r,
                    item,
                    '<font color=%s>%s</font>' % (self.colors[item](info),
                                                  info))

        r.message = r.getMessage()
        if self.usesTime() and not 'asctime' in self.colors:
            r.asctime = self.formatTime(record, self.datefmt)
        s = self._fmt.format(**r.__dict__)

        return s


class LoggerHandler(Handler):
    def __init__(self, parent):
        super(LoggerHandler, self).__init__()
        self.parent = parent

    def emit(self, record):
        self.parent.signal_new_log.emit(self.format(record))


def error_box(parent, msg, title='错误', buttons=QMessageBox.Ok):
    return QMessageBox.critical(parent, title, msg, buttons)


def warning_box(parent, msg, title='警告', buttons=QMessageBox.Ok):
    return QMessageBox.warning(parent, title, msg, buttons)

def info_box(parent, msg, title='提示', buttons=QMessageBox.Ok):
    return QMessageBox.information(parent, title, msg, buttons)


def human_readable(size, a_million_byte=1024 * 1024):
    if size > 1024 * a_million_byte:
        human_readable_size = '%.2f GB' % (size / (a_million_byte * 1024))
    elif size > a_million_byte:
        human_readable_size = '%.2f MB' % (size / a_million_byte)
    elif size > 1024:
        human_readable_size = '%.2f KB' % (size / 1024)
    else:
        human_readable_size = '%.2f B' % size

    return human_readable_size


class AsyncTaskMixin(QObject):

    signal_title_changed = Signal(str)
    signal_title_restored = Signal()
    signal_wait_dialog_show = Signal()
    signal_wait_dialog_hide = Signal()
    signal_label_changed = Signal(str)
    signal_label_restored = Signal()

    def setup_mixin(self, parent):
        self.wait_dialog = QDialog(parent)
        self.wait_dialog.setWindowTitle('请稍等')
        self.wait_label = QLabel('正在执行中...')
        layout = QVBoxLayout()
        layout.addWidget(self.wait_label)
        self.wait_dialog.setLayout(layout)
        self.wait_dialog.setModal(True)

        self.signal_wait_dialog_show.connect(self.wait_dialog.show)
        self.signal_wait_dialog_hide.connect(self.wait_dialog.hide)

        self.signal_title_changed.connect(
            lambda t: self.setWindowTitle('%s | %s' % (self.windowTitle(),
                                                       t))
        )

        self.signal_label_changed.connect(self.wait_label.setText)
        self.signal_label_restored.connect(
            lambda: self.wait_label.setText('正在执行中...')
        )

        self.signal_title_restored.connect(
            lambda: self.setWindowTitle(self.original_title)
        )

    def do_async_task(self, target,
                      signal_before=None, signal_after=None,
                      title_before='', title_after='',
                      block=True):
        def _():
            if title_before:
                self.signal_title_changed.emit(title_before)
                self.signal_label_changed.emit(title_before)

            if block:
                self.signal_wait_dialog_show.emit()

            if signal_before:
                signal_before.emit()

            ret = target()

            if title_after:
                self.signal_title_changed.emit(title_after)

            if signal_after:
                signal_after.emit(ret)

            if block:
                self.signal_wait_dialog_hide.emit()

            self.signal_title_restored.emit()
            self.signal_label_restored.emit()

        thread = threading.Thread(target=_)
        thread.start()

        return thread


def new_button(text, slot):
    btn = QPushButton(text)
    btn.clicked.connect(slot)

    return btn


def abnormal_standard_item(row):
    _ = QStandardItem()
    _.setCheckState(Qt.Checked if row.abnormal else Qt.Unchecked)
    _.setCheckable(False)
    _.setEditable(False)

    return _


def filter_empty_cluster_list(e):
    return e[e.cluster_list.map(lambda x: bool(x))]


class SortableStandardItemModel(QStandardItemModel):

    SortRole = Qt.UserRole + 10

    def __init__(self, parent, sort_types):
        super().__init__(parent=parent)

        self.sort_types = sort_types

    def data(self, idx, role=Qt.DisplayRole):
        if role == self.SortRole:
            row, col = idx.row(), idx.column()
            if not (0 <= col < self.columnCount()):
                return None
            if not (0 <= row < self.rowCount()):
                return None

            item = self.item(row, col)
            sort_type = self.sort_types[col]
            if sort_type == bool:
                return item.checkState() == Qt.Checked
            elif sort_type == str:
                return item.text()
            elif sort_type == int:
                return int(item.text())
            elif sort_type == datetime:
                text = item.text()
                if '.' in text:
                    return datetime.strptime(text, '%Y-%m-%d %H:%M:%S.%f')
                else:
                    return datetime.strptime(text, '%Y-%m-%d %H:%M:%S')
            else:
                return item.text()
        else:
            return super().data(idx, role)
