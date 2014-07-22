# encoding: utf-8

import matplotlib
matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4'] = 'PySide'
matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']

from PySide.QtGui import QApplication
import sys
from gui import MainWindow


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()

    window.show()
    app.exec_()
