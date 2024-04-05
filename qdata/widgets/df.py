"""
Module contains the data frame widgets.
"""

from PySide6.QtWidgets import QTableView, QWidget, QFrame
from PySide6.QtGui import QResizeEvent, QPaintEvent, QPainter, QColor
from PySide6.QtCore import Qt
from qdata.widgets.progress import Spinner

class LoadingOverlay(QWidget):
    """
    Loading overlay widget.
    """
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self._spinner = Spinner(self)
        self._spinner.setFixedHeight(32)
        self._spinner.adjustSize()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)

        size = self.size()
        self._spinner.move(int(size.width() / 2 - self._spinner.width() / 2), 10)

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)

        size = self.size()
        painter = QPainter()

        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setBrush(QColor(30, 30, 30, 75))
        painter.drawRect(0, 0, size.width(), size.height())
        painter.end()

class DataFrameTableView(QTableView):
    """
    Pandas data frame optimized table view.
    """
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.setSortingEnabled(True)
        self.setStyleSheet("QTableView {border: 1px solid #d4d4d4;}")
        self.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Raised)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectItems)
        self.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        self._loading = False

        self._loading_overlay = LoadingOverlay(self)
        self._loading_overlay.move(0, 0)
        self._loading_overlay.resize(self.width(), self.height())
        self._loading_overlay.hide()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)

        self._loading_overlay.move(0, 0)
        self._loading_overlay.resize(self.width(), self.height())

    @property
    def loading(self) -> bool:
        """
        Get the loading state.
        """
        return self._loading

    @loading.setter
    def loading(self, value: bool) -> None:
        """
        Set the loading state.
        """
        self._loading = value
        self._refresh()

    def _refresh(self) -> None:
        if self._loading:
            self._loading_overlay.show()
            self._loading_overlay.setEnabled(True)
        else:
            self._loading_overlay.hide()
            self._loading_overlay.setEnabled(False)
