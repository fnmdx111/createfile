# encoding: utf-8

from PySide.QtGui import *
from PySide.QtCore import *
from ..misc import ColoredFormatter, LoggerHandler


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
