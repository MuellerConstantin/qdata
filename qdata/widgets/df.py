"""
Module contains the data frame widgets.
"""

from typing import Union
import datetime as dt
from decimal import Decimal
from PySide6.QtWidgets import (QTableView, QWidget, QFrame, QDialog, QVBoxLayout, QButtonGroup, QRadioButton,
                               QLineEdit, QGridLayout, QDialogButtonBox, QSpacerItem, QSizePolicy, QGroupBox,
                               QComboBox, QLabel, QItemDelegate, QStyleOptionViewItem)
from PySide6.QtGui import QResizeEvent, QPaintEvent, QPainter, QColor, QUndoStack, QUndoCommand, QIcon
from PySide6.QtCore import Qt, Signal, QModelIndex
from qdata.widgets.progress import Spinner
from qdata.core.models.df import DataFrameTableModel, DataFrameSortFilterProxyModel, DataFrameItemDataRole

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

class DataFrameEditCellValueCommand(QUndoCommand):
    """
    Command for editing a data frame.
    """
    def __init__(self, model: Union[DataFrameTableModel, DataFrameSortFilterProxyModel],
                 row: int, col: int, old_value: object, new_value: object):
        super().__init__()

        self._model = model
        self._row = row
        self._col = col
        self._old_value = old_value
        self._new_value = new_value

    def undo(self):
        self._model.setData(self._model.index(self._row, self._col), self._old_value, DataFrameItemDataRole.DATA_ROLE)

    def redo(self):
        self._model.setData(self._model.index(self._row, self._col), self._new_value, DataFrameItemDataRole.DATA_ROLE)

class DataFrameRenameColumnCommand(QUndoCommand):
    """
    Command for renaming a column in a data frame.
    """
    def __init__(self, model: Union[DataFrameTableModel, DataFrameSortFilterProxyModel], col: int,
                 old_name: str, new_name: str):
        super().__init__()

        self._model = model
        self._col = col
        self._old_name = old_name
        self._new_name = new_name

    def undo(self):
        self._model.setHeaderData(self._col, Qt.Orientation.Horizontal, self._old_name, DataFrameItemDataRole.DATA_ROLE)

    def redo(self):
        self._model.setHeaderData(self._col, Qt.Orientation.Horizontal, self._new_name, DataFrameItemDataRole.DATA_ROLE)

class DataFrameInsertRowCommand(QUndoCommand):
    """
    Command for inserting a row in a data frame.
    """
    def __init__(self, model: Union[DataFrameTableModel, DataFrameSortFilterProxyModel], row: int):
        super().__init__()

        self._model = model
        self._row = row

        if isinstance(self._model, DataFrameSortFilterProxyModel):
            if self._row == self._model.rowCount():
                if self._row == self._model.sourceModel().rowCount():
                    self._source_row = self._model.sourceModel().rowCount()
                else:
                    self._source_row = self._model.mapToSource(self._model.index(self._row - 1, 0)).row() + 1
            else:
                self._source_row = self._model.mapToSource(self._model.index(self._row, 0)).row()
        else:
            self._source_row = self._row

    def undo(self):
        if isinstance(self._model, DataFrameSortFilterProxyModel):
            self._model.sourceModel().removeRow(self._source_row)
        else:
            self._model.removeRow(self._source_row)

    def redo(self):
        if isinstance(self._model, DataFrameSortFilterProxyModel):
            self._model.sourceModel().insertRow(self._source_row)
        else:
            self._model.insertRow(self._source_row)

class DataFrameRemoveRowCommand(QUndoCommand):
    """
    Command for removing a row in a data frame.
    """
    def __init__(self, model: Union[DataFrameTableModel, DataFrameSortFilterProxyModel], row: int):
        super().__init__()

        self._model = model
        self._row = row

        if isinstance(self._model, DataFrameSortFilterProxyModel):
            self._source_row = self._model.mapToSource(self._model.index(self._row, 0)).row()
            self._data = self._model.sourceModel().data(self._model.sourceModel().index(self._source_row, 0),
                                                        DataFrameItemDataRole.DATA_ROW_ROLE)
        else:
            self._source_row = self._row
            self._data = self._model.data(self._model.index(self._row, 0), DataFrameItemDataRole.DATA_ROW_ROLE)

    def undo(self):
        if isinstance(self._model, DataFrameSortFilterProxyModel):
            self._model.sourceModel().insertRow(self._source_row)
            self._model.sourceModel().setData(self._model.sourceModel().index(self._row, 0), self._data,
                                              DataFrameItemDataRole.DATA_ROW_ROLE)
        else:
            self._model.insertRow(self._source_row)
            self._model.setData(self._model.index(self._row, 0), self._data, DataFrameItemDataRole.DATA_ROW_ROLE)

    def redo(self):
        if isinstance(self._model, DataFrameSortFilterProxyModel):
            self._model.sourceModel().removeRow(self._source_row)
        else:
            self._model.removeRow(self._source_row)

class DataFrameInsertColumnCommand(QUndoCommand):
    """
    Command for inserting a column in a data frame.
    """
    def __init__(self, model: Union[DataFrameTableModel, DataFrameSortFilterProxyModel], col: int):
        super().__init__()

        self._model = model
        self._col = col

        if isinstance(self._model, DataFrameSortFilterProxyModel):
            if self._col == self._model.columnCount():
                if self._col == self._model.sourceModel().columnCount():
                    self._source_col = self._model.sourceModel().columnCount()
                else:
                    self._source_col = self._model.mapToSource(self._model.index(0, self._col - 1)).column() + 1
            else:
                self._source_col = self._model.mapToSource(self._model.index(0, self._col)).column()
        else:
            self._source_col = self._col

    def undo(self):
        if isinstance(self._model, DataFrameSortFilterProxyModel):
            self._model.sourceModel().removeColumn(self._source_col)
        else:
            self._model.removeColumn(self._source_col)

    def redo(self):
        if isinstance(self._model, DataFrameSortFilterProxyModel):
            self._model.sourceModel().insertColumn(self._source_col)
        else:
            self._model.insertColumn(self._source_col)

class DataFrameRemoveColumnCommand(QUndoCommand):
    """
    Command for removing a column in a data frame.
    """
    def __init__(self, model: Union[DataFrameTableModel, DataFrameSortFilterProxyModel], col: int):
        super().__init__()

        self._model = model
        self._col = col

        if isinstance(self._model, DataFrameSortFilterProxyModel):
            self._source_col = self._model.mapToSource(self._model.index(0, self._col)).column()
            self._data = self._model.sourceModel().data(self._model.sourceModel().index(0, self._source_col),
                                                        DataFrameItemDataRole.DATA_COLUMN_ROLE)
        else:
            self._source_col = self._col
            self._data = self._model.data(self._model.index(0, self._col), DataFrameItemDataRole.DATA_COLUMN_ROLE)

    def undo(self):
        if isinstance(self._model, DataFrameSortFilterProxyModel):
            self._model.sourceModel().insertColumn(self._source_col)
            self._model.sourceModel().setData(self._model.sourceModel().index(0, self._col), self._data,
                                              DataFrameItemDataRole.DATA_COLUMN_ROLE)
        else:
            self._model.insertColumn(self._source_col)
            self._model.setData(self._model.index(0, self._col), self._data, DataFrameItemDataRole.DATA_COLUMN_ROLE)

    def redo(self):
        if isinstance(self._model, DataFrameSortFilterProxyModel):
            self._model.sourceModel().removeColumn(self._source_col)
        else:
            self._model.removeColumn(self._source_col)

class DataFrameCellValueEditDialog(QDialog):
    """
    Data frame cell edit dialog.
    """
    def __init__(self, current_value: str, parent: QWidget = None):
        super().__init__(parent)

        self._value = None
        self._previous_value = current_value

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

        self._money_button = QRadioButton(self.tr("Money"))
        self._data_type_button_group.addButton(self._money_button)
        self._data_type_layout.addWidget(self._money_button, 2, 1)

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
        self._dialog_button_box.button(QDialogButtonBox.StandardButton.Apply).setDefault(True)
        self._dialog_button_box.button(QDialogButtonBox.StandardButton.Cancel).clicked.connect(self.reject)
        self._dialog_button_box.button(QDialogButtonBox.StandardButton.Cancel).setAutoDefault(False)
        self._central_layout.addWidget(self._dialog_button_box)

    @property
    def value(self) -> object:
        """
        Get the value.
        """
        return self._value

    @property
    def previous_value(self) -> str:
        """
        Get the previous value.
        """
        return self._previous_value

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
        elif self._money_button.isChecked():
            try:
                if self._format_combo_box.currentIndex() == 0:
                    self._value = Decimal.from_float(float(value.replace("$", "").replace(",", "")))
                elif self._format_combo_box.currentIndex() == 1:
                    self._value = Decimal.from_float(float(value.replace("€", "").replace(".", "").replace(",", ".")))
            except ValueError:
                self._error_label.setText(self.tr("Invalid money value."))
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
        elif button == self._money_button:
            self._format_combo_box.clear()
            self._format_combo_box.addItems(["Dollar ($ #,###.##)",
                                             "Euro (#.###,## €)"])

class DataFrameColumnNameEditDialog(QDialog):
    """
    Data frame header cell edit dialog.
    """
    def __init__(self, current_value: str, parent: QWidget = None):
        super().__init__(parent)

        self._value = None
        self._previous_value = current_value

        self.setWindowTitle(self.tr("Edit Column Name"))
        self.setFixedSize(400, 120)
        self.setWindowIcon(QIcon(":/favicons/favicon-dark.ico"))

        self._central_layout = QVBoxLayout()
        self._central_layout.setContentsMargins(10, 10, 10, 10)
        self._central_layout.setSpacing(10)
        self.setLayout(self._central_layout)

        self._title_label = QLabel(self.tr("Name"))
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

        self._central_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum,
                                                       QSizePolicy.Policy.MinimumExpanding))

        self._dialog_button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Apply |
                                                   QDialogButtonBox.StandardButton.Cancel)
        self._dialog_button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self._on_apply)
        self._dialog_button_box.button(QDialogButtonBox.StandardButton.Apply).setDefault(True)
        self._dialog_button_box.button(QDialogButtonBox.StandardButton.Cancel).clicked.connect(self.reject)
        self._dialog_button_box.button(QDialogButtonBox.StandardButton.Cancel).setAutoDefault(False)
        self._central_layout.addWidget(self._dialog_button_box)

    @property
    def value(self) -> object:
        """
        Get the value.
        """
        return self._value

    @property
    def previous_value(self) -> str:
        """
        Get the previous value.
        """
        return self._previous_value

    def _on_apply(self) -> None:
        """
        Apply the changes.
        """
        self._value = self._value_edit.text()
        self.accept()

class DataFrameItemDelegate(QItemDelegate):
    """
    Data frame item delegate.
    """
    def __init__(self, undo_stack: QUndoStack, parent: QWidget = None):
        super().__init__(parent)

        self._undo_stack = undo_stack

    def createEditor(self, parent: QWidget, _: QStyleOptionViewItem, index: QModelIndex) -> QWidget:
        current_value = index.data(Qt.ItemDataRole.DisplayRole)

        return DataFrameCellValueEditDialog(current_value, parent)

    def setModelData(self, editor: DataFrameCellValueEditDialog,
                     model: Union[DataFrameTableModel, DataFrameSortFilterProxyModel],
                     index: QModelIndex) -> None:
        if editor.result() == QDialog.DialogCode.Accepted:
            previous_value = editor.previous_value
            new_value = editor.value

            self._undo_stack.push(DataFrameEditCellValueCommand(model, index.row(), index.column(),
                                                       previous_value, new_value))

class DataFrameTableView(QTableView):
    """
    Pandas data frame optimized table view.
    """
    table_unsaved_changes = Signal(bool)
    table_undoable = Signal(bool)
    table_redoable = Signal(bool)
    table_begin_loading = Signal()
    table_end_loading = Signal()

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self._model: Union[DataFrameTableModel, DataFrameSortFilterProxyModel] = None

        self.setSortingEnabled(True)
        self.setStyleSheet("QTableView {border: 1px solid #d4d4d4;}")
        self.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Raised)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectItems)
        self.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.setCornerButtonEnabled(False)
        self.setEditTriggers(QTableView.EditTrigger.DoubleClicked)

        self._undo_stack = QUndoStack(self)
        self._undo_stack.canUndoChanged.connect(self.table_undoable)
        self._undo_stack.canRedoChanged.connect(self.table_redoable)
        self._undo_stack.cleanChanged.connect(lambda clean: self.table_unsaved_changes.emit(not clean))

        self._loading = False

        self._loading_overlay = LoadingOverlay(self)
        self._loading_overlay.move(0, 0)
        self._loading_overlay.resize(self.width(), self.height())
        self._loading_overlay.hide()

        self.setItemDelegate(DataFrameItemDelegate(self._undo_stack, self))
        self.horizontalHeader().sectionDoubleClicked.connect(self._on_horizontal_header_section_double_clicked)

    def _on_horizontal_header_section_double_clicked(self, index: int) -> None:
        column_name = self.model().headerData(index, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
        dialog = DataFrameColumnNameEditDialog(column_name, self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_column_name = dialog.value
            self._undo_stack.push(DataFrameRenameColumnCommand(self.model(), index, column_name, new_column_name))

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
            self.table_begin_loading.emit()
        else:
            self._loading_overlay.hide()
            self._loading_overlay.setEnabled(False)
            self.table_end_loading.emit()

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

    def setModel(self, model: Union[DataFrameTableModel, DataFrameSortFilterProxyModel]) -> None:
        super().setModel(model)

        self._model = model

        if self._model is not None:
            self._model.begin_transform.connect(self._on_begin_transform)
            self._model.end_transform.connect(self._on_end_transform)

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

    def insert_row(self, index: int) -> None:
        """
        Insert a row.
        """
        self._undo_stack.push(DataFrameInsertRowCommand(self.model(), index))

    def remove_row(self, index: int) -> None:
        """
        Remove a row.
        """
        self._undo_stack.push(DataFrameRemoveRowCommand(self.model(), index))

    def insert_column(self, index: int) -> None:
        """
        Insert a column.
        """
        self._undo_stack.push(DataFrameInsertColumnCommand(self.model(), index))

    def remove_column(self, index: int) -> None:
        """
        Remove a column.
        """
        self._undo_stack.push(DataFrameRemoveColumnCommand(self.model(), index))

    def _on_begin_transform(self) -> None:
        self.loading = True

    def _on_end_transform(self) -> None:
        self.loading = False
