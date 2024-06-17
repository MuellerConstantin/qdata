"""
Module containing the about dialog class and additional about related classes.
"""

import platform
import datetime
from PySide6.QtWidgets import (QDialog, QWidget, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy,
                               QDialogButtonBox, QTextEdit)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from qdata import __version__, __license_text__, __author__

class AboutDialog(QDialog):
    """
    Class that contains the about dialog.
    """
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.setWindowTitle("About")
        self.setFixedSize(400, 300)
        self.setWindowIcon(QIcon(":/favicons/favicon-dark.ico"))

        self._central_layout = QVBoxLayout()
        self.setLayout(self._central_layout)

        self._logo_label = QLabel()
        self._logo_label.setAlignment(Qt.AlignCenter)
        self._logo_pixmap = QIcon(":/images/logo-text-dark.png").pixmap(2048, 749)
        self._logo_label.setPixmap(self._logo_pixmap)
        self._logo_label.resizeEvent = lambda event: self._logo_label.setPixmap(self._logo_pixmap.scaled(event.size(),
                                                                        Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self._logo_label.setMaximumHeight(75)
        self._central_layout.addWidget(self._logo_label)

        self._central_layout.addSpacerItem(QSpacerItem(0, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        self._version_label = QLabel(f"Version: {__version__} ({platform.architecture()[0]} " +
                                     f"{platform.system()} {platform.release()})")
        self._version_label.setAlignment(Qt.AlignCenter)
        self._central_layout.addWidget(self._version_label)

        self._copyright_label = QLabel(f"© {datetime.datetime.now().year} {__author__}")
        self._copyright_label.setAlignment(Qt.AlignCenter)
        self._central_layout.addWidget(self._copyright_label)

        self._central_layout.addSpacerItem(QSpacerItem(0, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        self._license_text = QTextEdit()
        self._license_text.setReadOnly(True)
        self._license_text.setPlainText(__license_text__)
        self._central_layout.addWidget(self._license_text, 2)

        self._central_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum,
                                                       QSizePolicy.Policy.MinimumExpanding))

        self._dialog_button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        self._dialog_button_box.accepted.connect(self.accept)
        self._central_layout.addWidget(self._dialog_button_box)
