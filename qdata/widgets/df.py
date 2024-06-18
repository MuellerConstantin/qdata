"""
Module contains the data frame widgets.
"""

import datetime as dt
from PySide6.QtWidgets import (QTableView, QWidget, QFrame, QDialog, QVBoxLayout, QButtonGroup, QRadioButton,
                               QLineEdit, QGridLayout, QDialogButtonBox, QSpacerItem, QSizePolicy, QGroupBox,
                               QComboBox, QLabel, QItemDelegate, QStyleOptionViewItem)
from PySide6.QtGui import QResizeEvent, QPaintEvent, QPainter, QColor, QUndoStack, QUndoCommand, QIcon
from PySide6.QtCore import Qt, Signal, QModelIndex
from qdata.widgets.progress import Spinner
from qdata.core.models.df import DataFrameTableModel

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

class DataFrameEditCommand(QUndoCommand):
    """
    Command for editing a data frame.
    """
    def __init__(self, model: DataFrameTableModel, row: int, col: int, old_value: object, new_value: object):
        super().__init__()

        self._model = model
        self._row = row
        self._col = col
        self._old_value = old_value
        self._new_value = new_value

    def undo(self):
        self._model.setData(self._model.index(self._row, self._col), self._old_value, Qt.ItemDataRole.UserRole)

    def redo(self):
        self._model.setData(self._model.index(self._row, self._col), self._new_value, Qt.ItemDataRole.UserRole)

class DataFrameCellEditDialog(QDialog):
    """
    Data frame cell edit dialog.
    """
    def __init__(self, current_value: str, parent: QWidget = None):
        super().__init__(parent)

        self._value = None

        self.setWindowTitle(self.tr("Edit Value"))
        self.setFixedSize(400, 350)
        self.setWindowIcon(QIcon(":/favicons/favicon-dark.ico"))

        self._central_layout = QVBoxLayout()
        self._central_layout.setContentsMargins(10, 10, 10, 10)
        self._central_layout.setSpacing(10)
        self.setLayout(self._central_layout)

        self._title_label = QLabel(self.tr("Value"))
        self._title_label.setProperty("class", "title-label")
        self._central_layout.addWidget(self._title_label)

        self._value_edit_layout = QVBoxLayout()
        self._value_edit_layout.setContentsMargins(0, 0, 0, 0)
        self._value_edit_layout.setSpacing(2)
        self._central_layout.addLayout(self._value_edit_layout)

        self._value_edit = QLineEdit()
        self._value_edit.setProperty("class", "value-edit")
        self._value_edit.setMinimumHeight(30)
        self._value_edit.setText(current_value)
        self._value_edit.setPlaceholderText(self.tr("Enter value..."))
        self._value_edit_layout.addWidget(self._value_edit)

        self._error_label = QLabel()
        self._error_label.setProperty("class", "error-label")
        self._error_label.setVisible(False)
        self._value_edit_layout.addWidget(self._error_label)

        self._data_type_button_group = QButtonGroup(self)
        self._data_type_button_group.buttonClicked.connect(self._on_data_type_radio_button_clicked)
        self._data_type_layout = QGridLayout()
        self._data_type_group_box = QGroupBox(self.tr("Data Type"))
        self._data_type_group_box.setLayout(self._data_type_layout)
        self._central_layout.addWidget(self._data_type_group_box)

        self._text_button = QRadioButton(self.tr("Text"))
        self._text_button.setChecked(True)
        self._data_type_button_group.addButton(self._text_button)
        self._data_type_layout.addWidget(self._text_button, 0, 0)

        self._integer_button = QRadioButton(self.tr("Integer"))
        self._data_type_button_group.addButton(self._integer_button)
        self._data_type_layout.addWidget(self._integer_button, 0, 1)

        self._real_button = QRadioButton(self.tr("Real"))
        self._data_type_button_group.addButton(self._real_button)
        self._data_type_layout.addWidget(self._real_button, 0, 2)

        self._time_button = QRadioButton(self.tr("Time"))
        self._data_type_button_group.addButton(self._time_button)
        self._data_type_layout.addWidget(self._time_button, 1, 0)

        self._date_button = QRadioButton(self.tr("Date"))
        self._data_type_button_group.addButton(self._date_button)
        self._data_type_layout.addWidget(self._date_button, 1, 1)

        self._datetime_button = QRadioButton(self.tr("Timestamp"))
        self._data_type_button_group.addButton(self._datetime_button)
        self._data_type_layout.addWidget(self._datetime_button, 1, 2)

        self._duration_button = QRadioButton(self.tr("Duration"))
        self._data_type_button_group.addButton(self._duration_button)
        self._data_type_layout.addWidget(self._duration_button, 2, 0)

        self._format_group_box = QGroupBox(self.tr("Format"))
        self._format_layout = QVBoxLayout()
        self._format_group_box.setLayout(self._format_layout)
        self._central_layout.addWidget(self._format_group_box)

        self._format_combo_box = QComboBox()
        self._format_layout.addWidget(self._format_combo_box)

        self._central_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum,
                                                       QSizePolicy.Policy.MinimumExpanding))

        self._dialog_button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Apply |
                                                   QDialogButtonBox.StandardButton.Cancel)
        self._dialog_button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self._on_apply)
        self._dialog_button_box.button(QDialogButtonBox.StandardButton.Cancel).clicked.connect(self.reject)
        self._central_layout.addWidget(self._dialog_button_box)

    @property
    def value(self) -> object:
        """
        Get the value.
        """
        return self._value

    def _on_apply(self) -> None:
        """
        Apply the changes.
        """
        value = self._value_edit.text()

        if self._text_button.isChecked():
            self._value = value
        elif self._integer_button.isChecked():
            try:
                if self._format_combo_box.currentIndex() == 0:
                    self._value = int(value)
                elif self._format_combo_box.currentIndex() == 1:
                    self._value = int(value.replace(",", ""))
                elif self._format_combo_box.currentIndex() == 2:
                    self._value = int(value.replace(".", ""))
            except ValueError:
                self._error_label.setText(self.tr("Invalid integer value."))
                self._error_label.setVisible(True)
                return
        elif self._real_button.isChecked():
            try:
                if self._format_combo_box.currentIndex() == 0:
                    self._value = float(value.replace(",", ""))
                elif self._format_combo_box.currentIndex() == 1:
                    self._value = float(value.replace(".", "").replace(",", "."))
            except ValueError:
                self._error_label.setText(self.tr("Invalid real value."))
                self._error_label.setVisible(True)
                return
        elif self._time_button.isChecked():
            try:
                if self._format_combo_box.currentIndex() == 0:
                    self._value = dt.datetime.strptime(value, "%H:%M:%S").time()
                elif self._format_combo_box.currentIndex() == 1:
                    self._value = dt.datetime.strptime(value, "%H:%M").time()
                elif self._format_combo_box.currentIndex() == 2:
                    self._value = dt.datetime.strptime(value, "%I:%M:%S %p").time()
                elif self._format_combo_box.currentIndex() == 3:
                    self._value = dt.datetime.strptime(value, "%I:%M %p").time()
            except ValueError:
                self._error_label.setText(self.tr("Invalid time value."))
                self._error_label.setVisible(True)
                return
        elif self._date_button.isChecked():
            try:
                if self._format_combo_box.currentIndex() == 0:
                    self._value = dt.datetime.strptime(value, "%Y-%m-%d").date()
                elif self._format_combo_box.currentIndex() == 1:
                    self._value = dt.datetime.strptime(value, "%d.%m.%Y").date()
            except ValueError:
                self._error_label.setText(self.tr("Invalid date value."))
                self._error_label.setVisible(True)
                return
        elif self._datetime_button.isChecked():
            try:
                if self._format_combo_box.currentIndex() == 0:
                    self._value = dt.datetime.strptime(value, "%Y-%m-%d %I:%M:%S %p")
                elif self._format_combo_box.currentIndex() == 1:
                    self._value = dt.datetime.strptime(value, "%Y-%m-%d %I:%M %p")
                elif self._format_combo_box.currentIndex() == 2:
                    self._value = dt.datetime.strptime(value, "%d.%m.%Y %H:%M:%S")
                elif self._format_combo_box.currentIndex() == 3:
                    self._value = dt.datetime.strptime(value, "%d.%m.%Y %H:%M")
            except ValueError:
                self._error_label.setText(self.tr("Invalid timestamp value."))
                self._error_label.setVisible(True)
                return
        elif self._duration_button.isChecked():
            try:
                if self._format_combo_box.currentIndex() == 0:
                    days = value.split(" ")[0]
                    time = value.split(" ")[1]
                    hours = time.split(":")[0]
                    minutes = time.split(":")[1]
                    seconds = time.split(":")[2]

                    self._value = dt.timedelta(days=int(days),
                                               hours=int(hours),
                                               minutes=int(minutes),
                                               seconds=int(seconds))
            except (ValueError, IndexError, TypeError):
                self._error_label.setText(self.tr("Invalid duration value."))
                self._error_label.setVisible(True)
                return

        self.accept()

    def _on_data_type_radio_button_clicked(self, button: QRadioButton) -> None:
        if button == self._text_button:
            self._format_combo_box.clear()
            self._format_combo_box.setEnabled(False)
        elif button == self._integer_button:
            self._format_combo_box.clear()
            self._format_combo_box.addItems(["No Group Separator (####)",
                                             "Comma Group Separator (#,###)",
                                             "Dot Group Separator (#.###)"])
            self._format_combo_box.setEnabled(True)
        elif button == self._real_button:
            self._format_combo_box.clear()
            self._format_combo_box.addItems(["Decimal Dot (#,###.##)",
                                             "Decimal Comma (#.###,##)"])
            self._format_combo_box.setEnabled(True)
        elif button == self._time_button:
            self._format_combo_box.clear()
            self._format_combo_box.addItems(["HH:MM:SS",
                                             "HH:MM",
                                             "HH:MM:SS AM/PM",
                                             "HH:MM AM/PM"])
            self._format_combo_box.setEnabled(True)
        elif button == self._date_button:
            self._format_combo_box.clear()
            self._format_combo_box.addItems(["YYYY-MM-DD",
                                             "DD.MM.YYYY"])
            self._format_combo_box.setEnabled(True)
        elif button == self._datetime_button:
            self._format_combo_box.clear()
            self._format_combo_box.addItems(["YYYY-MM-DD HH:MM:SS AM/PM",
                                             "YYYY-MM-DD HH:MM AM/PM",
                                             "DD.MM.YYYY HH:MM:SS",
                                             "DD.MM.YYYY HH:MM"])
            self._format_combo_box.setEnabled(True)
        elif button == self._duration_button:
            self._format_combo_box.clear()
            self._format_combo_box.addItems(["D HH:MM:SS"])
            self._format_combo_box.setEnabled(True)

class DataFrameItemDelegate(QItemDelegate):
    """
    Data frame item delegate.
    """
    def createEditor(self, parent: QWidget, _: QStyleOptionViewItem, index: QModelIndex) -> QWidget:
        current_value = index.data(Qt.ItemDataRole.DisplayRole)

        return DataFrameCellEditDialog(current_value, parent)

    def setModelData(self, editor: QWidget, model: DataFrameTableModel, index: QModelIndex) -> None:
        if editor.result() == QDialog.DialogCode.Accepted:
            model.setData(index, editor.value, Qt.ItemDataRole.EditRole)

class DataFrameTableView(QTableView):
    """
    Pandas data frame optimized table view.
    """
    table_unsaved_changes = Signal(bool)
    table_undoable = Signal(bool)
    table_redoable = Signal(bool)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.setSortingEnabled(True)
        self.setStyleSheet("QTableView {border: 1px solid #d4d4d4;}")
        self.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Raised)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectItems)
        self.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        self._undo_stack = QUndoStack(self)
        self._undo_stack.canUndoChanged.connect(self.table_undoable)
        self._undo_stack.canRedoChanged.connect(self.table_redoable)
        self._undo_stack.cleanChanged.connect(lambda clean: self.table_unsaved_changes.emit(not clean))

        self._loading = False

        self._loading_overlay = LoadingOverlay(self)
        self._loading_overlay.move(0, 0)
        self._loading_overlay.resize(self.width(), self.height())
        self._loading_overlay.hide()

        self.setItemDelegate(DataFrameItemDelegate(self))

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

        if self._loading:
            self._loading_overlay.show()
            self._loading_overlay.setEnabled(True)
        else:
            self._loading_overlay.hide()
            self._loading_overlay.setEnabled(False)

    @property
    def undoable(self) -> bool:
        """
        Get the undoable state.
        """
        return self._undo_stack.canUndo()

    @property
    def redoable(self) -> bool:
        """
        Get the redoable state.
        """
        return self._undo_stack.canRedo()

    @property
    def unsaved_changes(self) -> bool:
        """
        Get the unsaved changes state.
        """
        return not self._undo_stack.isClean()

    def setModel(self, model: DataFrameTableModel) -> None:
        super().setModel(model)

        if model is not None:
            model.data_edited.connect(self._on_data_edit)

    def undo(self) -> None:
        """
        Undo the last action.
        """
        self._undo_stack.undo()

    def redo(self) -> None:
        """
        Redo the last action.
        """
        self._undo_stack.redo()

    def mark_saved(self) -> None:
        """
        Mark the current state as saved.
        """
        self._undo_stack.setClean()

    def _on_data_edit(self, row: int, col: int, old_value: object, new_value: object) -> None:
        self._undo_stack.push(DataFrameEditCommand(self.model(), row, col, old_value, new_value))
