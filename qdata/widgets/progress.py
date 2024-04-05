"""
Module that contains the loading and progress widgets.
"""

from PySide6.QtGui import QPaintEvent, QPainter, QColor, QPen
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QSize, Qt, QTimer

class Spinner(QWidget):
    """
    Widget that shows a loading spinner.
    """
    def __init__(self, parent: QWidget = None):
        super(Spinner, self).__init__(parent)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_timeout)

        self._progress = 0.6
        self._thickness = 4
        self._angle = 0

        self._timer.start(10)

    def sizeHint(self) -> QSize:
        return QSize(32, 32)

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        track_pen = QPen()
        track_pen.setWidth(4)
        track_pen.setColor(QColor("#d4d4d4"))
        track_pen.setCapStyle(Qt.RoundCap)
        track_pen.setJoinStyle(Qt.RoundJoin)
        track_pen.setStyle(Qt.SolidLine)

        trail_pen = QPen()
        trail_pen.setWidth(4)
        trail_pen.setColor(QColor("#16a34a"))
        trail_pen.setCapStyle(Qt.RoundCap)
        trail_pen.setJoinStyle(Qt.RoundJoin)
        trail_pen.setStyle(Qt.SolidLine)

        size = min(self.width(), self.height())
        x = (self.width() - size) / 2
        y = (self.height() - size) / 2

        painter.setPen(track_pen)
        painter.drawEllipse(x + (self._thickness // 2), y + (self._thickness // 2),
                            size - self._thickness, size - self._thickness)

        painter.setPen(trail_pen)
        painter.drawArc(x + (self._thickness // 2), y + (self._thickness // 2),
                        size - self._thickness, size - self._thickness,
                        -self._angle * 16, -self._progress * 360 * 16)

    def _on_timeout(self):
        self._angle += 1
        self.update()
