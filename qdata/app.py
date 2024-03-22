"""
Module that contains the main application and window classes.
"""

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PySide6.QtGui import QIcon
from PySide6.QtCore import QFile, Qt
from qdata import __version__

# pylint: disable-next=unused-import
import qdata.resources

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

        self._central_widget = QWidget()
        self._central_layout = QVBoxLayout()
        self._central_layout.setContentsMargins(0, 0, 0, 0)
        self._central_widget.setLayout(self._central_layout)
        self.setCentralWidget(self._central_widget)

    def _init_menu_bar(self):
        self._file_menu = self.menuBar().addMenu("&File")
        self._edit_menu = self.menuBar().addMenu("&Edit")
        self._help_menu = self.menuBar().addMenu("&Help")

        # Initialize file menu actions

        self._new_window_action = self._file_menu.addAction("&New Window")
        self._new_window_action.setShortcut("Ctrl+N")
        self._new_window_action.setToolTip("Open a new window")

        self._file_menu.addSeparator()

        self._exit_action = self._file_menu.addAction("&Exit")
        self._exit_action.setShortcut("Ctrl+Q")
        self._exit_action.setToolTip("Exit the application")
        self._exit_action.triggered.connect(self.close)

        # Initialize edit menu actions

        self._copy_action = self._edit_menu.addAction("&Copy")
        self._copy_action.setShortcut("Ctrl+C")
        self._copy_action.setToolTip("Copy the selected content")

        # Initialize help menu actions

        self._about_action = self._help_menu.addAction("&About")
        self._about_action.setToolTip("About the application")

    def _init_tool_bar(self):
        pass

    def _init_status_bar(self):
        self.statusBar().showMessage("Ready")

class Application(QApplication):
    """
    Main application class that initializes the main window and starts the event loop.
    """
    def __init__(self, argv):
        super().__init__(argv)

        self.setApplicationName("QData")
        self.setApplicationDisplayName("QData")
        self.setApplicationVersion(__version__)
        self.setStyle("Fusion")

        self._main_window = MainWindow()
        self._main_window.show()
