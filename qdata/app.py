"""
Module that contains the main application and window classes.
"""

import os
from multiprocessing import Process
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget, QFileDialog
from PySide6.QtGui import QIcon
from PySide6.QtCore import QFile, QDir, Qt
from qdata import __version__, __app_name__
from qdata.widgets.about import AboutDialog

# pylint: disable-next=unused-import
import qdata.resources

def _run_new_window_process():
    """
    Run a new window process.
    """
    app = Application([])
    app.exec()

class MainWindow(QMainWindow):
    """
    Main window class that contains the main application window.
    """
    def __init__(self):
        super().__init__(None, Qt.WindowType.Window)

        self.setWindowTitle("QData")
        self.setMinimumSize(600, 400)
        self.setWindowIcon(QIcon(":/favicons/favicon-dark.ico"))

        style_sheet_file = QFile(":/styles/global.qss")
        style_sheet_file.open(QFile.ReadOnly)
        self.setStyleSheet(style_sheet_file.readAll().toStdString())
        style_sheet_file.close()

        self._init_menu_bar()
        self._init_tool_bar()
        self._init_status_bar()

        # Initialize central widget

        self._central_widget = QWidget()
        self._central_layout = QVBoxLayout()
        self._central_layout.setContentsMargins(0, 0, 0, 0)
        self._central_widget.setLayout(self._central_layout)
        self.setCentralWidget(self._central_widget)

        # Initialize tab widget

        self._tab_widget = QTabWidget()
        self._tab_widget.setDocumentMode(True)
        self._tab_widget.setTabsClosable(True)
        self._tab_widget.setMovable(True)
        self._tab_widget.setUsesScrollButtons(True)
        self._tab_widget.tabCloseRequested.connect(self._on_tab_close_requested)
        self._central_layout.addWidget(self._tab_widget)

    def _init_menu_bar(self):
        """
        Initialize the menu bar with menus and actions.
        """
        self._file_menu = self.menuBar().addMenu(self.tr("&File"))
        self._edit_menu = self.menuBar().addMenu(self.tr("&Edit"))
        self._help_menu = self.menuBar().addMenu(self.tr("&Help"))

        # Initialize file menu actions

        self._new_window_action = self._file_menu.addAction(self.tr("&New Window"))
        self._new_window_action.setShortcut("Ctrl+N")
        self._new_window_action.setToolTip(self.tr("Open a new window"))
        self._new_window_action.triggered.connect(self._on_new_window)

        self._file_menu.addSeparator()

        self._open_file_action = self._file_menu.addAction(self.tr("&Open File..."))
        self._open_file_action.setShortcut("Ctrl+O")
        self._open_file_action.setToolTip(self.tr("Open a file"))
        self._open_file_action.triggered.connect(self._on_open_file)

        self._file_menu.addSeparator()

        self._exit_action = self._file_menu.addAction(self.tr("&Exit"))
        self._exit_action.setShortcut("Ctrl+Q")
        self._exit_action.setToolTip(self.tr("Exit the application"))
        self._exit_action.triggered.connect(self._on_exit)

        # Initialize edit menu actions

        self._copy_action = self._edit_menu.addAction(self.tr("&Copy"))
        self._copy_action.setShortcut("Ctrl+C")
        self._copy_action.setToolTip(self.tr("Copy selected text"))

        # Initialize help menu actions

        self._about_action = self._help_menu.addAction(self.tr("&About"))
        self._about_action.setToolTip(self.tr("Show the about dialog"))
        self._about_action.triggered.connect(self._on_about)

    def _init_tool_bar(self):
        """
        Initialize the toolbar with actions and widgets.
        """

    def _init_status_bar(self):
        """
        Initialize the status bar with widgets and labels.
        """
        self.statusBar().showMessage("Ready")

    def _on_new_window(self):
        """
        Open a new window. Technically, this will start a new process with the same application.
        """
        new_window_process = Process(target=_run_new_window_process)
        new_window_process.start()

    def _on_open_file(self):
        """
        Open a file dialog to open a file.
        """
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter(self.tr("QVD Files (*.qvd)"))
        file_dialog.setDirectory(QDir.homePath())
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)

        file_dialog_result = file_dialog.exec()

        if file_dialog_result:
            file_path = file_dialog.selectedFiles()[0]
            file_name = os.path.basename(file_path)

            if self._is_file_already_open(file_path):
                tab_index = self._get_tab_index_by_file_path(file_path)
                self._tab_widget.setCurrentIndex(tab_index)
                return

            tab_index = self._tab_widget.addTab(QWidget(), file_name)
            self._tab_widget.tabBar().setTabToolTip(tab_index, file_path)
            self._tab_widget.tabBar().setTabData(tab_index, file_path)
            self._tab_widget.setCurrentIndex(tab_index)

    def _on_exit(self):
        """
        Exit the application.
        """
        self.close()

    def _on_about(self):
        """
        Show the about dialog.
        """
        about_dialog = AboutDialog(self)
        about_dialog.exec()

    def _on_tab_close_requested(self, index: int):
        """
        Close the tab at the given index.
        """
        self._tab_widget.removeTab(index)

    def _get_tab_index_by_file_path(self, file_path: str) -> int:
        """
        Get the tab index by the file path. If the file is not open in any tab, return -1.
        """
        for index in range(self._tab_widget.count()):
            tab_text = self._tab_widget.tabText(index)

            if tab_text == file_path:
                return index

        return -1

    def _is_file_already_open(self, file_path: str) -> bool:
        """
        Check if the file is already open in a tab.
        """
        return self._get_tab_index_by_file_path(file_path) != -1

class Application(QApplication):
    """
    Main application class that initializes the main window and starts the event loop.
    """
    def __init__(self, argv):
        super().__init__(argv)

        self.setApplicationName(__app_name__)
        self.setApplicationDisplayName(__app_name__)
        self.setApplicationVersion(__version__)
        self.setStyle("Fusion")

        self._main_window = MainWindow()
        self._main_window.show()
