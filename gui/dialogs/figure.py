# encoding: utf-8
from PySide.QtCore import *
from PySide.QtGui import *
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg, \
    NavigationToolbar2QTAgg


class FigureDialog(QDialog):
    def __init__(self, parent, figure, title='绘图结果'):
        super().__init__(parent=parent)

        self.setWindowTitle(title)
        self.setWindowFlags(self.windowFlags() |
                            Qt.WindowMaximizeButtonHint)

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
