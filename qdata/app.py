"""
Module that contains the main application and window classes.
"""

import os
import functools
from multiprocessing import Process
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
                               QTabWidget, QFileDialog, QSpacerItem, QSizePolicy)
from PySide6.QtGui import QIcon
from PySide6.QtCore import QFile, QDir, Qt, QSettings
from qdata import __version__, __app_name__, __organization__
from qdata.widgets.qvd import QvdFileWidget
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
        self._tab_widget.currentChanged.connect(self._on_tab_changed)
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

        self._recent_files_menu = self._file_menu.addMenu(self.tr("&Open Recent File"))
        recent_files = list(QSettings(QSettings.Scope.UserScope).value("recentFiles", [], list))
        self._on_recent_files_changed(recent_files)
        self._recent_files_menu.setEnabled(bool(recent_files))

        self._file_menu.addSeparator()

        self._exit_action = self._file_menu.addAction(self.tr("&Exit"))
        self._exit_action.setShortcut("Ctrl+Q")
        self._exit_action.setToolTip(self.tr("Exit the application"))
        self._exit_action.triggered.connect(self._on_exit)

        # Initialize edit menu actions

        self._copy_action = self._edit_menu.addAction(self.tr("&Copy"))
        self._copy_action.setShortcut("Ctrl+C")
        self._copy_action.setToolTip(self.tr("Copy selected text"))
        self._copy_action.setEnabled(False)
        self._copy_action.triggered.connect(self._on_copy)

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
        self._status_widget = QWidget()
        self._status_layout = QHBoxLayout()
        self._status_layout.setContentsMargins(10, 5, 10, 5)
        self._status_layout.setSpacing(36)
        self._status_widget.setLayout(self._status_layout)
        self.statusBar().addPermanentWidget(self._status_widget, 1)
        self.statusBar().setSizeGripEnabled(False)

        self._status_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        # Initialize table filtered shape status

        self._table_filtered_shape_widget = QWidget()
        self._table_filtered_shape_widget.setVisible(False)
        self._table_filtered_shape_layout = QHBoxLayout()
        self._table_filtered_shape_layout.setContentsMargins(0, 0, 0, 0)
        self._table_filtered_shape_widget.setLayout(self._table_filtered_shape_layout)
        self._status_layout.addWidget(self._table_filtered_shape_widget)

        self._table_filtered_shape_titel_label = QLabel()
        self._table_filtered_shape_titel_label.setText(self.tr("Filtered"))
        self._table_filtered_shape_layout.addWidget(self._table_filtered_shape_titel_label)

        self._table_filtered_shape_icon = QLabel()
        self._table_filtered_shape_icon.setPixmap(QIcon(":/icons/table-green-600.svg").pixmap(12, 12))
        self._table_filtered_shape_layout.addWidget(self._table_filtered_shape_icon)

        self._table_filtered_shape_label = QLabel()
        self._table_filtered_shape_label.setText("7x233")
        self._table_filtered_shape_layout.addWidget(self._table_filtered_shape_label)

        # Initialize table full shape status

        self._table_full_shape_widget = QWidget()
        self._table_full_shape_widget.setVisible(False)
        self._table_full_shape_layout = QHBoxLayout()
        self._table_full_shape_layout.setContentsMargins(0, 0, 0, 0)
        self._table_full_shape_widget.setLayout(self._table_full_shape_layout)
        self._status_layout.addWidget(self._table_full_shape_widget)

        self._table_full_shape_titel_label = QLabel()
        self._table_full_shape_titel_label.setText(self.tr("Full"))
        self._table_full_shape_layout.addWidget(self._table_full_shape_titel_label)

        self._table_full_shape_icon = QLabel()
        self._table_full_shape_icon.setPixmap(QIcon(":/icons/table-neutral-800.svg").pixmap(12, 12))
        self._table_full_shape_layout.addWidget(self._table_full_shape_icon)

        self._table_full_shape_label = QLabel()
        self._table_full_shape_label.setText("7x233")
        self._table_full_shape_layout.addWidget(self._table_full_shape_label)

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
            self._on_open_qvd_file(file_path)

    def _on_exit(self):
        """
        Exit the application.
        """
        self.close()

    def _on_copy(self):
        """
        Copy the selected text.
        """
        current_tab_widget = self._tab_widget.currentWidget()

        if current_tab_widget:
            selected_value = current_tab_widget.get_selected_value()
            QApplication.clipboard().setText(str(selected_value))

    def _on_about(self):
        """
        Show the about dialog.
        """
        about_dialog = AboutDialog(self)
        about_dialog.exec()

    def _on_tab_changed(self, index: int):
        """
        Called when the tab is changed.
        """
        if index == -1:
            self._table_full_shape_widget.setVisible(False)
            self._table_filtered_shape_widget.setVisible(False)
            self._copy_action.setEnabled(False)
            return

        self._copy_action.setEnabled(True)

        current_tab_widget = self._tab_widget.widget(index)

        if current_tab_widget.loaded:
            self._table_full_shape_label.setText(
                f"{current_tab_widget.get_table_shape()[1]}x{current_tab_widget.get_table_shape()[0]}")
            self._table_full_shape_widget.setVisible(True)
        else:
            self._table_full_shape_widget.setVisible(False)

        if current_tab_widget.loaded and current_tab_widget.is_filtered():
            self._table_filtered_shape_label.setText(f"{current_tab_widget.get_filtered_table_shape()[1]}x" +
                                                     f"{current_tab_widget.get_filtered_table_shape()[0]}")
            self._table_filtered_shape_widget.setVisible(True)
        else:
            self._table_filtered_shape_widget.setVisible(False)

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
            tab_data = self._tab_widget.tabBar().tabData(index)

            if tab_data == file_path:
                return index

        return -1

    def _is_file_already_open(self, file_path: str) -> bool:
        """
        Check if the file is already open in a tab.
        """
        return self._get_tab_index_by_file_path(file_path) != -1

    def _on_table_loaded(self, qvd_file_widget: QvdFileWidget):
        """
        Called when the table is loaded.
        """
        current_tab_widget = self._tab_widget.currentWidget()

        if current_tab_widget == qvd_file_widget:
            self._table_full_shape_label.setText(
                f"{qvd_file_widget.get_table_shape()[1]}x{qvd_file_widget.get_table_shape()[0]}")
            self._table_full_shape_widget.setVisible(True)

    def _on_table_filtered(self, qvd_file_widget: QvdFileWidget):
        """
        Called when the table is filtered.
        """
        current_tab_widget = self._tab_widget.currentWidget()

        if current_tab_widget == qvd_file_widget:
            if qvd_file_widget.is_filtered():
                self._table_filtered_shape_label.setText(f"{qvd_file_widget.get_filtered_table_shape()[1]}x" +
                                                         f"{qvd_file_widget.get_filtered_table_shape()[0]}")
                self._table_filtered_shape_widget.setVisible(True)
            else:
                self._table_filtered_shape_widget.setVisible(False)

    def _on_table_errored(self, qvd_file_widget: QvdFileWidget):
        """
        Called when the table is errored.
        """
        current_tab_widget = self._tab_widget.currentWidget()

        if current_tab_widget == qvd_file_widget:
            self._table_full_shape_widget.setVisible(False)
            self._table_filtered_shape_widget.setVisible(False)

        # Remove file from recent files list
        settings = QSettings(QSettings.Scope.UserScope)
        recent_files = list(QSettings(QSettings.Scope.UserScope).value("recentFiles", [], list))

        try:
            recent_files.remove(qvd_file_widget.path)
            settings.setValue('recentFiles', recent_files)
            self._on_recent_files_changed(recent_files)
        except ValueError:
            pass

    def _on_table_loading(self, qvd_file_widget: QvdFileWidget):
        """
        Called when the table is loading.
        """
        current_tab_widget = self._tab_widget.currentWidget()

        if current_tab_widget == qvd_file_widget:
            self._table_full_shape_widget.setVisible(False)
            self._table_filtered_shape_widget.setVisible(False)

    def _on_recent_files_changed(self, recent_files: list):
        """
        Called when the recent files list is changed.
        """
        self._recent_files_menu.clear()

        # pylint: disable-next=invalid-name
        MAX_RECENT_FILES = 5

        for _, recent_file in enumerate(recent_files[:MAX_RECENT_FILES]):
            action = self._recent_files_menu.addAction(recent_file)
            action.setToolTip(recent_file)
            action.triggered.connect(functools.partial(self._on_open_recent_file, recent_file))

        self._recent_files_menu.addSeparator()

        clear_recent_files_action = self._recent_files_menu.addAction(self.tr("Clear Recent Files"))
        clear_recent_files_action.triggered.connect(self._on_clear_recent_files)

        self._recent_files_menu.setEnabled(bool(recent_files))

    def _on_clear_recent_files(self):
        """
        Clear the recent files list.
        """
        settings = QSettings(QSettings.Scope.UserScope)
        settings.setValue('recentFiles', [])

        self._on_recent_files_changed([])

    def _on_open_recent_file(self, file_path: str):
        """
        Open a recent file.
        """
        self._on_open_qvd_file(file_path)

    def _on_open_qvd_file(self, file_path: str):
        """
        Open a QVD file.
        """
        if self._is_file_already_open(file_path):
            tab_index = self._get_tab_index_by_file_path(file_path)
            self._tab_widget.setCurrentIndex(tab_index)
            return

        file_name = os.path.basename(file_path)

        qvd_file_widget = QvdFileWidget(file_path)
        qvd_file_widget.tableLoaded.connect(lambda: self._on_table_loaded(qvd_file_widget))
        qvd_file_widget.tableFiltered.connect(lambda: self._on_table_filtered(qvd_file_widget))
        qvd_file_widget.tableErrored.connect(lambda: self._on_table_errored(qvd_file_widget))
        qvd_file_widget.tableLoading.connect(lambda: self._on_table_loading(qvd_file_widget))
        tab_index = self._tab_widget.addTab(qvd_file_widget, file_name)
        self._tab_widget.tabBar().setTabToolTip(tab_index, file_path)
        self._tab_widget.tabBar().setTabData(tab_index, file_path)
        self._tab_widget.setCurrentIndex(tab_index)

        # Update recent files list
        settings = QSettings(QSettings.Scope.UserScope)
        recent_files = list(QSettings(QSettings.Scope.UserScope).value("recentFiles", [], list))

        try:
            recent_files.remove(file_path)
        except ValueError:
            pass

        recent_files.insert(0, str(file_path))
        settings.setValue('recentFiles', recent_files)

        self._on_recent_files_changed(recent_files)

class Application(QApplication):
    """
    Main application class that initializes the main window and starts the event loop.
    """
    def __init__(self, argv):
        super().__init__(argv)

        QSettings.setDefaultFormat(QSettings.Format.IniFormat)

        self.setApplicationName(__app_name__)
        self.setOrganizationName(__organization__)
        self.setApplicationDisplayName(__app_name__)
        self.setApplicationVersion(__version__)
        self.setStyle("Fusion")

        self._main_window = MainWindow()
        self._main_window.show()
