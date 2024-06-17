"""
This module contains the welcome widget.
"""

import os
import functools
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QPushButton,
                               QCommandLinkButton, QScrollArea)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, Signal, QSettings, QSize

class WelcomeWidget(QWidget):
    """
    The welcome widget.
    """
    open_file = Signal()
    open_recent = Signal(str)
    import_csv_file = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._central_layout = QHBoxLayout()
        self._central_layout.setContentsMargins(0, 0, 0, 0)
        self._central_layout.setSpacing(25)
        self.setLayout(self._central_layout)

        # Initialize the sidebar widget

        self._sidebar_widget = QWidget()
        self._sidebar_widget_size_policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self._sidebar_widget_size_policy.setHorizontalStretch(1)
        self._sidebar_widget_size_policy.setVerticalStretch(1)
        self._sidebar_widget.setSizePolicy(self._sidebar_widget_size_policy)
        self._sidebar_widget.setMinimumWidth(250)
        self._sidebar_widget.setMaximumWidth(600)
        self._sidebar_widget.setProperty("class", "welcome-sidebar")
        self._central_layout.addWidget(self._sidebar_widget)

        self._sidebar_layout = QVBoxLayout()
        self._sidebar_layout.setContentsMargins(10, 10, 10, 10)
        self._sidebar_layout.setSpacing(10)
        self._sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self._sidebar_widget.setLayout(self._sidebar_layout)

        self._recent_files_label = QLabel(self.tr("Recent Files"))
        self._recent_files_label.setProperty("class", "recent-files-label")
        self._sidebar_layout.addWidget(self._recent_files_label)

        self._no_recent_files_label = QLabel(self.tr("No recent files."))
        self._no_recent_files_label.setProperty("class", "no-recent-files-label")
        self._no_recent_files_label.setVisible(False)
        self._sidebar_layout.addWidget(self._no_recent_files_label)

        self._recent_files_scroll_area = QScrollArea()
        self._recent_files_scroll_area.setProperty("class", "recent-files-scroll-area")
        self._recent_files_scroll_area.setWidgetResizable(True)
        self._recent_files_scroll_area.setVisible(False)
        self._sidebar_layout.addWidget(self._recent_files_scroll_area)

        self._recent_files_widget = QWidget()
        self._recent_files_widget.setProperty("class", "recent-files-container")
        self._recent_files_layout = QVBoxLayout()
        self._recent_files_layout.setContentsMargins(0, 0, 0, 0)
        self._recent_files_layout.setSpacing(10)
        self._recent_files_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self._recent_files_widget.setLayout(self._recent_files_layout)
        self._recent_files_scroll_area.setWidget(self._recent_files_widget)

        recent_files = list(QSettings(QSettings.Scope.UserScope).value("recentFiles", [], list))

        if not recent_files:
            self._no_recent_files_label.setVisible(True)
        else:
            self._recent_files_scroll_area.setVisible(True)

        for file in recent_files:
            file_name = os.path.basename(file)
            recent_file_button = QPushButton(file_name)
            recent_file_button.setProperty("class", "recent-file-button")
            recent_file_button.setFlat(True)
            recent_file_button.setToolTip(file)
            recent_file_button.setIcon(QIcon(":/icons/qvd-file.svg"))
            recent_file_button.setIconSize(QSize(18, 18))
            recent_file_button.clicked.connect(functools.partial(self.open_recent.emit, file))
            self._recent_files_layout.addWidget(recent_file_button)

        # Initialize the content widget

        self._content_widget = QWidget()
        self._content_widget.setProperty("class", "welcome-content")
        self._content_widget_size_policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self._content_widget_size_policy.setHorizontalStretch(3)
        self._sidebar_widget_size_policy.setVerticalStretch(1)
        self._content_widget.setSizePolicy(self._content_widget_size_policy)
        self._central_layout.addWidget(self._content_widget)

        self._content_layout = QVBoxLayout()
        self._content_layout.setContentsMargins(10, 25, 10, 25)
        self._content_layout.setSpacing(25)
        self._content_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self._content_widget.setLayout(self._content_layout)

        self._header_layout = QVBoxLayout()
        self._header_layout.setContentsMargins(0, 0, 0, 0)
        self._header_layout.setSpacing(5)
        self._header_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self._content_layout.addLayout(self._header_layout)

        self._logo_label = QLabel()
        self._logo_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self._logo_pixmap = QIcon(":/images/logo-text-dark.png").pixmap(2048, 749)
        self._logo_label.setPixmap(self._logo_pixmap)
        self._logo_label.resizeEvent = lambda event: self._logo_label.setPixmap(self._logo_pixmap.scaled(event.size(),
                                                                        Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self._logo_label.setMaximumHeight(75)
        self._header_layout.addWidget(self._logo_label)

        self._welcome_label = QLabel("Welcome to QData!")
        self._welcome_label.setProperty("class", "welcome-label")
        self._header_layout.addWidget(self._welcome_label)

        self._actions_layout = QVBoxLayout()
        self._actions_layout.setContentsMargins(0, 0, 0, 0)
        self._actions_layout.setSpacing(5)
        self._actions_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self._content_layout.addLayout(self._actions_layout)

        self._start_label = QLabel(self.tr("Start"))
        self._start_label.setProperty("class", "start-label")
        self._actions_layout.addWidget(self._start_label)

        self._open_file_button = QCommandLinkButton(self.tr("Open File"))
        self._open_file_button.setDescription("Open a file to start working with QData.")
        self._open_file_button.setIcon(QIcon(":/icons/file-circle-plus-green-600.svg"))
        self._open_file_button_size_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._open_file_button.setSizePolicy(self._open_file_button_size_policy)
        self._open_file_button.setMaximumWidth(400)
        self._open_file_button.clicked.connect(self.open_file.emit)
        self._actions_layout.addWidget(self._open_file_button)

        self._import_csv_file_button = QCommandLinkButton(self.tr("Import CSV File"))
        self._import_csv_file_button.setDescription("Import a CSV file to start working with QData.")
        self._import_csv_file_button.setIcon(QIcon(":/icons/file-import-green-600.svg"))
        self._import_csv_file_button_size_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._import_csv_file_button.setSizePolicy(self._import_csv_file_button_size_policy)
        self._import_csv_file_button.setMaximumWidth(400)
        self._import_csv_file_button.clicked.connect(self.import_csv_file.emit)
        self._actions_layout.addWidget(self._import_csv_file_button)

    def update_recent_files(self):
        """
        Update the list of recent files.
        """
        for index in reversed(range(self._recent_files_layout.count())):
            self._recent_files_layout.itemAt(index).widget().deleteLater()

        recent_files = list(QSettings(QSettings.Scope.UserScope).value("recentFiles", [], list))

        if not recent_files:
            self._no_recent_files_label.setVisible(True)
            self._recent_files_scroll_area.setVisible(False)
        else:
            self._no_recent_files_label.setVisible(False)
            self._recent_files_scroll_area.setVisible(True)

            for file in recent_files:
                file_name = os.path.basename(file)
                recent_file_button = QPushButton(file_name)
                recent_file_button.setProperty("class", "recent-file-button")
                recent_file_button.setFlat(True)
                recent_file_button.setToolTip(file)
                recent_file_button.setIcon(QIcon(":/icons/qvd-file.svg"))
                recent_file_button.setIconSize(QSize(18, 18))
                recent_file_button.clicked.connect(functools.partial(self.open_recent.emit, file))
                self._recent_files_layout.addWidget(recent_file_button)
