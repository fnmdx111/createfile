# encoding: utf-8
from PySide.QtGui import *

from drive.fs.fat32 import FAT32
from drive.fs.ntfs import NTFS
from .dialogs import LogDialog, PartitionsDialog
from .sub_windows import NTFSSubWindow, FAT32SubWindow
from .misc import AsyncTaskMixin, human_readable, new_button
from .widgets import RulesWidget, ColumnListView


class MainWindow(QMainWindow):

    USE_TAB_MODE = False

    def __init__(self):
        super().__init__(parent=None)

        self.setWindowTitle('Apollō - 面向数字取证的时间真实性分析工具')
        self.setWindowIcon(QFileIconProvider().icon(QFileIconProvider.Trashcan))

        self.mdi_area = QMdiArea()
        if self.USE_TAB_MODE:
            self.mdi_area.setViewMode(QMdiArea.TabbedView)
            self.mdi_area.setTabsClosable(True)
            self.mdi_area.setTabsMovable(True)

        self.setCentralWidget(self.mdi_area)

        self.mdi_area.subWindowActivated.connect(self.update_actions)

        self.partition_dialog = PartitionsDialog(parent=self)

        self.setup_menus()

    def setup_menus(self):
        file_menu = self.menuBar().addMenu('文件(&F)')

        open_partition_action = QAction('打开分区(&O)...', self)
        open_partition_action.setIcon(
            QFileIconProvider().icon(QFileIconProvider.Folder)
        )
        open_partition_action.setShortcut(QKeySequence.Open)
        open_partition_action.setStatusTip('打开一个分区以进行分析')
        open_partition_action.triggered.connect(self.open_partition)
        file_menu.addAction(open_partition_action)

        file_menu.addSeparator()

        exit_action = QAction('退出(&X)', self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.setStatusTip('退出createfile')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        window_menu = self.menuBar().addMenu('窗口(&W)')
        cascade_windows_action = QAction('层叠窗口(&C)', self)
        cascade_windows_action.triggered.connect(self.mdi_area.cascadeSubWindows)
        window_menu.addAction(cascade_windows_action)

        tile_windows_action = QAction('平铺窗口(&T)', self)
        tile_windows_action.triggered.connect(self.mdi_area.tileSubWindows)
        window_menu.addAction(tile_windows_action)

    def open_partition(self):
        accepted = self.partition_dialog.exec_()
        if accepted:
            partition = self.partition_dialog.current_partition()
            partition_address =\
                self.partition_dialog.current_partition_address_text()

            if partition.type == FAT32.type:
                sub_window = FAT32SubWindow(self, partition,
                                            partition_address)
            elif partition.type == NTFS.type:
                sub_window = NTFSSubWindow(self, partition,
                                           partition_address)
            else:
                sub_window = None

            if sub_window:
                sub_window = self.mdi_area.addSubWindow(sub_window)
                sub_window.setWindowIcon(
                    QFileIconProvider().icon(QFileIconProvider.Drive)
                )
                sub_window.show()

    def update_actions(self, sub_window):
        pass
