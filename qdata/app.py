"""
Module that contains the main application and window classes.
"""

import os
import functools
from multiprocessing import Process
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
                               QTabWidget, QTabBar, QFileDialog, QSpacerItem, QSizePolicy, QPushButton,
                               QMessageBox)
from PySide6.QtGui import QIcon
from PySide6.QtCore import QFile, QDir, Qt, QSettings
from qdata import __version__, __app_name__, __organization__
from qdata.widgets.qvd import QvdFileWidget
from qdata.widgets.about import AboutDialog
from qdata.widgets.welcome import WelcomeWidget

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

        self.resize(800, 600)

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

        # Initialize welcome widget

        self._welcome_widget = WelcomeWidget()
        self._welcome_widget.open_file.connect(self._on_open_file)
        self._welcome_widget.open_recent.connect(self._on_open_recent_file)

        tab_index = self._tab_widget.addTab(self._welcome_widget, "Welcome")
        self._tab_widget.tabBar().setTabToolTip(tab_index, "Welcome to QData")
        self._tab_widget.tabBar().setTabIcon(tab_index, QIcon(":/favicons/favicon-dark.ico"))
        self._tab_widget.setCurrentIndex(tab_index)

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

        self._save_file_action = self._file_menu.addAction(self.tr("&Save"))
        self._save_file_action.setShortcut("Ctrl+S")
        self._save_file_action.setToolTip(self.tr("Save the current file"))
        self._save_file_action.setEnabled(False)
        self._save_file_action.triggered.connect(self._on_save)

        self._save_as_file_action = self._file_menu.addAction(self.tr("Save &As..."))
        self._save_as_file_action.setShortcut("Ctrl+Shift+S")
        self._save_as_file_action.setToolTip(self.tr("Save the current file as..."))
        self._save_as_file_action.setEnabled(False)
        self._save_as_file_action.triggered.connect(self._on_save_as)

        self._file_menu.addSeparator()

        self._export_menu = self._file_menu.addMenu(self.tr("&Export"))
        self._export_menu.setToolTip(self.tr("Export the current table"))
        self._export_menu.setEnabled(False)

        self._export_to_csv_action = self._export_menu.addAction(self.tr("&CSV..."))
        self._export_to_csv_action.setToolTip(self.tr("Export the current table as a CSV file"))
        self._export_to_csv_action.triggered.connect(self._on_export_to_csv)

        self._file_menu.addSeparator()

        self._close_file_action = self._file_menu.addAction(self.tr("&Close File"))
        self._close_file_action.setShortcut("Ctrl+F4")
        self._close_file_action.setToolTip(self.tr("Close the current file"))
        self._close_file_action.setEnabled(False)
        self._close_file_action.triggered.connect(self._on_close_file)

        self._file_menu.addSeparator()

        self._exit_action = self._file_menu.addAction(self.tr("&Exit"))
        self._exit_action.setShortcut("Ctrl+Q")
        self._exit_action.setToolTip(self.tr("Exit the application"))
        self._exit_action.triggered.connect(self._on_exit)

        # Initialize edit menu actions

        self._undo_action = self._edit_menu.addAction(self.tr("&Undo"))
        self._undo_action.setShortcut("Ctrl+Z")
        self._undo_action.setToolTip(self.tr("Undo the last action"))
        self._undo_action.setEnabled(False)
        self._undo_action.triggered.connect(self._on_undo)

        self._redo_action = self._edit_menu.addAction(self.tr("&Redo"))
        self._redo_action.setShortcut("Ctrl+Y")
        self._redo_action.setToolTip(self.tr("Redo the last action"))
        self._redo_action.setEnabled(False)
        self._redo_action.triggered.connect(self._on_redo)

        self._edit_menu.addSeparator()

        self._copy_action = self._edit_menu.addAction(self.tr("&Copy"))
        self._copy_action.setShortcut("Ctrl+C")
        self._copy_action.setToolTip(self.tr("Copy selected text"))
        self._copy_action.setEnabled(False)
        self._copy_action.triggered.connect(self._on_copy)

        # Initialize help menu actions

        self._welcome_action = self._help_menu.addAction(self.tr("&Welcome"))
        self._welcome_action.setToolTip(self.tr("Show the welcome tab"))
        self._welcome_action.triggered.connect(self._on_welcome)

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

    def _on_save(self):
        """
        Save the current file.
        """
        current_tab_index = self._tab_widget.currentIndex()

        if current_tab_index == -1:
            return

        current_tab_widget = self._tab_widget.widget(current_tab_index)
        current_tab_widget.save()

    def _on_save_as(self):
        """
        Save the current file as a new file.
        """
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter(self.tr("QVD Files (*.qvd)"))
        file_dialog.setDirectory(QDir.homePath())
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)

        file_dialog_result = file_dialog.exec()

        if file_dialog_result:
            file_path = file_dialog.selectedFiles()[0]
            current_tab_index = self._tab_widget.currentIndex()
            current_tab_widget = self._tab_widget.widget(current_tab_index)
            current_tab_widget.save(file_path)

    def _on_export_to_csv(self):
        """
        Export the current table as a CSV file.
        """
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter(self.tr("CSV Files (*.csv)"))
        file_dialog.setDirectory(QDir.homePath())
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)

        file_dialog_result = file_dialog.exec()

        if file_dialog_result:
            file_path = file_dialog.selectedFiles()[0]
            current_tab_index = self._tab_widget.currentIndex()
            current_tab_widget = self._tab_widget.widget(current_tab_index)
            current_tab_widget.export_to_csv(file_path)

    def _on_close_file(self):
        """
        Close the current file.
        """
        current_tab_index = self._tab_widget.currentIndex()

        if current_tab_index == -1:
            return

        self._tab_widget.removeTab(current_tab_index)

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

    def _on_undo(self):
        """
        Undo the last action.
        """
        current_tab_widget = self._tab_widget.currentWidget()

        if current_tab_widget:
            current_tab_widget.undo()

    def _on_redo(self):
        """
        Redo the last action.
        """
        current_tab_widget = self._tab_widget.currentWidget()

        if current_tab_widget:
            current_tab_widget.redo()

    def _on_welcome(self):
        """
        Show the welcome tab.
        """
        if self._is_welcome_tab_already_open():
            welcome_tab_index = self._get_welcome_tab_index()
            self._tab_widget.setCurrentIndex(welcome_tab_index)
            return

        welcome_tab_index = self._tab_widget.addTab(self._welcome_widget, "Welcome")
        self._tab_widget.tabBar().setTabToolTip(welcome_tab_index, "Welcome to QData")
        self._tab_widget.tabBar().setTabIcon(welcome_tab_index, QIcon(":/favicons/favicon-dark.ico"))
        self._tab_widget.setCurrentIndex(welcome_tab_index)

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
        if index == -1 or self._tab_widget.widget(index) == self._welcome_widget:
            self._table_full_shape_widget.setVisible(False)
            self._table_filtered_shape_widget.setVisible(False)
            self._copy_action.setEnabled(False)
            self._close_file_action.setEnabled(False)
            self._undo_action.setEnabled(False)
            self._redo_action.setEnabled(False)
            self._save_file_action.setEnabled(False)
            self._save_as_file_action.setEnabled(False)
            self._export_menu.setEnabled(False)

            return

        current_tab_widget = self._tab_widget.widget(index)

        # Update actions depending on widget state
        self._copy_action.setEnabled(current_tab_widget.loaded)
        self._close_file_action.setEnabled(True)
        self._undo_action.setEnabled(current_tab_widget.undoable)
        self._redo_action.setEnabled(current_tab_widget.redoable)
        self._save_file_action.setEnabled(current_tab_widget.unsaved_changes)
        self._save_as_file_action.setEnabled(current_tab_widget.loaded)
        self._export_menu.setEnabled(current_tab_widget.loaded)

        # Update base table shape status
        if current_tab_widget.loaded:
            self._table_full_shape_label.setText(
                f"{current_tab_widget.get_table_shape()[1]}x{current_tab_widget.get_table_shape()[0]}")
            self._table_full_shape_widget.setVisible(True)
        else:
            self._table_full_shape_widget.setVisible(False)

        # Update filtered table shape status
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
        current_tab_widget = self._tab_widget.widget(index)

        if current_tab_widget == self._welcome_widget or not current_tab_widget.unsaved_changes:
            self._tab_widget.removeTab(index)
            return

        message_box = QMessageBox(self)
        message_box.setIcon(QMessageBox.Icon.Question)
        message_box.setWindowTitle(self.tr("Unsaved Changes"))
        message_box.setText(self.tr("Your changes will be lost if you don't save them. Do you want " +
                                    "to save the changes?"))
        message_box.setStandardButtons(QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard |
                                        QMessageBox.StandardButton.Cancel)
        message_box.setDefaultButton(QMessageBox.StandardButton.Save)

        decision = message_box.exec()

        if decision == QMessageBox.StandardButton.Discard:
            self._tab_widget.removeTab(index)
        elif decision == QMessageBox.StandardButton.Save:
            current_tab_widget.save()

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

    def _get_welcome_tab_index(self) -> int:
        """
        Get the welcome tab index. If the welcome tab is not open, return -1.
        """
        for index in range(self._tab_widget.count()):
            tab_widget = self._tab_widget.widget(index)

            if tab_widget == self._welcome_widget:
                return index

        return -1

    def _is_welcome_tab_already_open(self) -> bool:
        """
        Check if the welcome tab is already open.
        """
        return self._get_welcome_tab_index() != -1

    def _on_table_loaded(self, qvd_file_widget: QvdFileWidget):
        """
        Called when the table is loaded.
        """
        current_tab_widget = self._tab_widget.currentWidget()

        if current_tab_widget == qvd_file_widget:
            self._table_full_shape_label.setText(
                f"{qvd_file_widget.get_table_shape()[1]}x{qvd_file_widget.get_table_shape()[0]}")
            self._table_full_shape_widget.setVisible(True)

            self._copy_action.setEnabled(True)
            self._save_as_file_action.setEnabled(True)
            self._export_menu.setEnabled(True)

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

    def _on_table_undoable(self, undoable: bool, qvd_file_widget: QvdFileWidget):
        """
        Called when the table is undoable.
        """
        current_tab_widget = self._tab_widget.currentWidget()

        if current_tab_widget == qvd_file_widget:
            self._undo_action.setEnabled(undoable)

    def _on_table_redoable(self, redoable: bool, qvd_file_widget: QvdFileWidget):
        """
        Called when the table is redoable.
        """
        current_tab_widget = self._tab_widget.currentWidget()

        if current_tab_widget == qvd_file_widget:
            self._redo_action.setEnabled(redoable)

    def _on_table_unsaved_changes(self, unsaved_changes: bool, qvd_file_widget: QvdFileWidget):
        """
        Called when the table has unsaved changes.
        """
        tab_index = self._tab_widget.indexOf(qvd_file_widget)
        close_button = self._tab_widget.tabBar().tabButton(tab_index, QTabBar.ButtonPosition.RightSide)

        if unsaved_changes:
            close_button.setProperty("role", "unsaved-changes")
        else:
            close_button.setProperty("role", "close")

        close_button.style().polish(close_button)

        current_tab_widget = self._tab_widget.currentWidget()

        if current_tab_widget == qvd_file_widget:
            self._save_file_action.setEnabled(unsaved_changes)
            self._save_as_file_action.setEnabled(True)

    def _on_table_path_changed(self, path: str, qvd_file_widget: QvdFileWidget):
        """
        Called when the table path is changed.
        """
        tab_index = self._tab_widget.indexOf(qvd_file_widget)
        file_name = os.path.basename(path)

        self._tab_widget.tabBar().setTabToolTip(tab_index, path)
        self._tab_widget.setTabText(tab_index, file_name)

        # Update recent files list
        settings = QSettings(QSettings.Scope.UserScope)
        recent_files = list(QSettings(QSettings.Scope.UserScope).value("recentFiles", [], list))

        try:
            recent_files.remove(path)
        except ValueError:
            pass

        recent_files.insert(0, str(path))
        settings.setValue('recentFiles', recent_files)

        self._on_recent_files_changed(recent_files)

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

        if hasattr(self, "_welcome_widget") and self._welcome_widget:
            self._welcome_widget.update_recent_files()

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

        qvd_file_widget = QvdFileWidget()
        qvd_file_widget.table_loaded.connect(lambda: self._on_table_loaded(qvd_file_widget))
        qvd_file_widget.table_filtered.connect(lambda: self._on_table_filtered(qvd_file_widget))
        qvd_file_widget.table_loading_errored.connect(lambda: self._on_table_errored(qvd_file_widget))
        qvd_file_widget.table_loading.connect(lambda: self._on_table_loading(qvd_file_widget))
        qvd_file_widget.table_undoable.connect(lambda undoable: self._on_table_undoable(undoable, qvd_file_widget))
        qvd_file_widget.table_redoable.connect(lambda redoable: self._on_table_redoable(redoable, qvd_file_widget))
        qvd_file_widget.table_unsaved_changes.connect(
            lambda unsaved_changes: self._on_table_unsaved_changes(unsaved_changes, qvd_file_widget))
        qvd_file_widget.table_path_changed.connect(lambda path: self._on_table_path_changed(path, qvd_file_widget))
        qvd_file_widget.load(file_path)

        tab_index = self._tab_widget.addTab(qvd_file_widget, file_name)
        self._tab_widget.tabBar().setTabToolTip(tab_index, file_path)
        self._tab_widget.tabBar().setTabData(tab_index, file_path)
        self._tab_widget.tabBar().setTabIcon(tab_index, QIcon(":/icons/qvd-file.svg"))

        close_button = QPushButton(self)
        close_button.setProperty("role", "close")
        close_button.setToolTip(self.tr("Close Tab"))
        close_button.clicked.connect(lambda: self._tab_widget.tabBar()
                                     .tabCloseRequested.emit(self._tab_widget.indexOf(qvd_file_widget)))
        self._tab_widget.tabBar().setTabButton(tab_index, QTabBar.ButtonPosition.RightSide, close_button)

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
