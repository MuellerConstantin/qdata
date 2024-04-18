"""
Contains table related widgets.
"""

from PySide6.QtWidgets import (QFrame, QWidget, QHBoxLayout, QLabel, QPushButton,
                               QScrollArea, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon
from qdata.core.models.transform import DataFrameFilter, DataFrameFilterOperation

class FilterTag(QFrame):
    """
    Tag widget that represents a tag.
    """
    close = Signal()

    def __init__(self, filter_: DataFrameFilter, parent: QWidget = None):
        super().__init__(parent)

        self._filter = filter_

        self.setMinimumWidth(150)
        self.setMaximumWidth(200)
        self.setFixedHeight(30)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Raised)
        self.setStyleSheet("background-color: #ffffff;")
        self.setToolTip(f"{self._get_operator_text(self._filter.operation)} '{self._filter.value}'")

        self._central_layout = QHBoxLayout()
        self._central_layout.setContentsMargins(5, 5, 5, 5)
        self._central_layout.setSpacing(5)
        self.setLayout(self._central_layout)

        self._icon_label = QLabel()
        self._icon_label.setPixmap(QIcon(":/icons/filter-neutral-800.svg").pixmap(12, 12))
        self._central_layout.addWidget(self._icon_label)

        self._title_label = QLabel()
        self._title_label.setText(self._filter.column)
        self._central_layout.addWidget(self._title_label, 1)

        self._close_button = QPushButton()
        self._close_button.setIconSize(QSize(16, 16))
        self._close_button.setStyleSheet("QPushButton {padding: 0; border: 0; " +
                                         "qproperty-icon: url(:/icons/xmark-neutral-800.svg);}")
        self._close_button.setToolTip("Remove Filter")
        self._close_button.clicked.connect(self.close.emit)
        self._central_layout.addWidget(self._close_button)

    @property
    def filter(self) -> DataFrameFilter:
        """
        Get the filter.
        """
        return self._filter

    def _get_operator_text(self, operator: DataFrameFilterOperation) -> str:
        """
        Get the text representation of a filter operator.
        """
        if operator == DataFrameFilterOperation.EQUAL:
            return "Equal"
        elif operator == DataFrameFilterOperation.NOT_EQUAL:
            return "Not Equal"
        elif operator == DataFrameFilterOperation.GREATER_THAN:
            return "Greater Than"
        elif operator == DataFrameFilterOperation.GREATER_THAN_OR_EQUAL:
            return "Greater Than or Equal"
        elif operator == DataFrameFilterOperation.LESS_THAN:
            return "Less Than"
        elif operator == DataFrameFilterOperation.LESS_THAN_OR_EQUAL:
            return "Less Than or Equal"

class FilterTagView(QWidget):
    """
    Widget that displays tags.
    """
    empty = Signal()
    add = Signal(DataFrameFilter)
    remove = Signal(DataFrameFilter)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self._central_layout = QHBoxLayout()
        self._central_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._central_layout)

        self._scroll_area = QScrollArea()
        self._scroll_area.setFixedHeight(60)
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._central_layout.addWidget(self._scroll_area)

        self._tag_container_layout = QHBoxLayout()
        self._tag_container_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._tag_container_layout.setContentsMargins(10, 5, 10, 5)

        self._spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self._tag_container_layout.addSpacerItem(self._spacer)

        self._tag_container = QWidget()
        self._tag_container.setLayout(self._tag_container_layout)
        self._scroll_area.setWidget(self._tag_container)

    def get_tag_at(self, index: int) -> FilterTag:
        """
        Get a tag by index.
        """
        return self._tag_container_layout.itemAt(index).widget()

    def add_tag(self, tag: FilterTag):
        """
        Add a tag to the view.
        """
        self._tag_container_layout.insertWidget(self._tag_container_layout.count() - 1, tag)
        self.add.emit(tag.filter)

    def remove_tag(self, tag: FilterTag):
        """
        Remove a tag from the view.
        """
        self._tag_container_layout.removeWidget(tag)
        tag.setParent(None)
        self.remove.emit(tag.filter)

        if self._tag_container_layout.count() == 1:
            self.empty.emit()

    def remove_tag_at(self, index: int):
        """
        Remove a tag from the view.
        """
        tag = self.get_tag_at(index)
        self.remove_tag(tag)
