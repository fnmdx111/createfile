# encoding: utf-8
from PySide.QtCore import *
from PySide.QtGui import *
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg, \
    NavigationToolbar2QTAgg


class FigureWidget(QWidget):
    def __init__(self, parent, figure, parameters=None):
        super().__init__(parent=parent)

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

        self.parameters = parameters
