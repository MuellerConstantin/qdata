"""
Contains widgets for displaying QVD files.
"""

from typing import Tuple
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QSpacerItem, QSizePolicy, QLabel,
                               QMenu, QApplication, QDialog, QLineEdit, QDialogButtonBox,
                               QStackedWidget, QGridLayout)
from PySide6.QtCore import QThreadPool, Qt, QPoint, Signal
from PySide6.QtGui import QIcon
import pandas as pd
from qdata.widgets.progress import Spinner
from qdata.widgets.filter import FilterTagView, FilterTag
from qdata.widgets.df import DataFrameTableView
from qdata.core.models.df import DataFrameTableModel
from qdata.core.models.transform import DataFrameFilter, DataFrameFilterOperation
from qdata.parallel.qvd import LoadQvdFileTask

class QvdFileFieldValuesDialog(QDialog):
    """
    Dialog for displaying field values.
    """
    filtered = Signal(DataFrameFilter)

    def __init__(self, column: str, field_values: pd.DataFrame, parent: QWidget = None):
        super().__init__(parent)

        self._column = column
        self._field_values = field_values
        self._table_model = DataFrameTableModel(self._field_values)
        self._table_model.end_filtering.connect(self._on_table_model_end_filtering)
        self._current_filter = None

        self.setWindowTitle(self.tr("Field Values"))
        self.setFixedSize(300, 400)
        self.setWindowIcon(QIcon(":/favicons/favicon-dark.ico"))

        self._central_layout = QVBoxLayout()
        self._central_layout.setContentsMargins(10, 10, 10, 10)
        self._central_layout.setSpacing(10)
        self.setLayout(self._central_layout)

        self._column_name_label = QLabel(self._column)
        self._column_name_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self._column_name_label.setStyleSheet("font-size: 16px; font-weight: semi-bold;")
        self._central_layout.addWidget(self._column_name_label)

        self._search_line_edit = QLineEdit()
        self._search_line_edit.addAction(QIcon(":/icons/magnifying-glass-green-600.svg"),
                                         QLineEdit.ActionPosition.LeadingPosition)
        self._search_line_edit.setPlaceholderText(self.tr("Search..."))
        self._search_line_edit.textChanged.connect(self._on_search_line_edit_text_changed)
        self._central_layout.addWidget(self._search_line_edit)

        self._table_view = DataFrameTableView()
        self._table_view.horizontalHeader().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._table_view.customContextMenuRequested.connect(self._on_data_context_menu)
        self._table_view.setSelectionBehavior(DataFrameTableView.SelectionBehavior.SelectRows)
        self._table_view.setModel(self._table_model)
        self._central_layout.addWidget(self._table_view, 1)

        self._kpi_layout = QGridLayout()
        self._kpi_layout.setContentsMargins(0, 0, 0, 0)
        self._kpi_layout.setSpacing(5)
        self._central_layout.addLayout(self._kpi_layout)

        self._total_values_label = QLabel(self.tr("Total Values: ") + str(len(self._field_values)))
        self._total_values_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self._kpi_layout.addWidget(self._total_values_label, 0, 0)

        self._found_values_label = QLabel(self.tr("Found Values: ") + str(len(self._field_values)))
        self._found_values_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self._kpi_layout.addWidget(self._found_values_label, 1, 0)

        self._central_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum,
                                                       QSizePolicy.Policy.MinimumExpanding))

        self._dialog_button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        self._dialog_button_box.accepted.connect(self.accept)
        self._central_layout.addWidget(self._dialog_button_box)

    def _on_search_line_edit_text_changed(self, text: str):
        """
        Handle the search line edit text changed.
        """
        if self._current_filter is not None:
            self._table_model.remove_filter(self._current_filter)

        self._current_filter = DataFrameFilter(self.tr("Value"), DataFrameFilterOperation.BEGINS_WITH, text)
        self._table_model.add_filter(self._current_filter)

    def _on_table_model_end_filtering(self):
        """
        Handle the table model ending to filter.
        """
        self._found_values_label.setText(self.tr("Found Values: ") + str(len(self._table_model.df)))

    def _on_data_context_menu_copy(self, pos: QPoint):
        """
        Handle the context menu copy action.
        """
        selected_index = self._table_view.indexAt(pos)
        column_value = self._table_model.df.iloc[selected_index.row(), selected_index.column()]
        QApplication.clipboard().setText(str(column_value))

    def _on_data_context_menu_filter(self, pos: QPoint, operation: DataFrameFilterOperation):
        """
        Handle the context menu filter action.
        """
        selected_index = self._table_view.indexAt(pos)
        value_column_index = self._table_model.df.columns.get_loc(self.tr("Value"))
        column_value = self._table_model.df.iloc[selected_index.row(), value_column_index]

        self.filtered.emit(DataFrameFilter(self._column, operation, column_value))
        self.accept()

    def _on_data_context_menu(self, pos: QPoint):
        """
        Handle the data context menu.
        """
        menu = QMenu(self)

        copy_action = menu.addAction(self.tr("Copy"))
        copy_action.triggered.connect(lambda: self._on_data_context_menu_copy(pos))

        menu.addSeparator()

        filter_menu = menu.addMenu(self.tr("Filter"))

        filter_equal_action = filter_menu.addAction(self.tr("Equal"))
        filter_equal_action.triggered.connect(
            lambda: self._on_data_context_menu_filter(pos, DataFrameFilterOperation.EQUAL))

        filter_not_equal_action = filter_menu.addAction(self.tr("Not Equal"))
        filter_not_equal_action.triggered.connect(
            lambda: self._on_data_context_menu_filter(pos, DataFrameFilterOperation.NOT_EQUAL))

        filter_greater_action = filter_menu.addAction(self.tr("Greater Than"))
        filter_greater_action.triggered.connect(
            lambda: self._on_data_context_menu_filter(pos, DataFrameFilterOperation.GREATER_THAN))

        filter_greater_equal_action = filter_menu.addAction(self.tr("Greater Than or Equal"))
        filter_greater_equal_action.triggered.connect(
            lambda: self._on_data_context_menu_filter(pos, DataFrameFilterOperation.GREATER_THAN_OR_EQUAL))

        filter_less_action = filter_menu.addAction(self.tr("Less Than"))
        filter_less_action.triggered.connect(
            lambda: self._on_data_context_menu_filter(pos, DataFrameFilterOperation.LESS_THAN))

        filter_less_equal_action = filter_menu.addAction(self.tr("Less Than or Equal"))
        filter_less_equal_action.triggered.connect(
            lambda: self._on_data_context_menu_filter(pos, DataFrameFilterOperation.LESS_THAN_OR_EQUAL))

        menu.exec(self._table_view.mapToGlobal(pos))

class QvdFileDataView(QWidget):
    """
    Widget that represents a QVD file data view.
    """
    tableFiltered = Signal()

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self._table_model: DataFrameTableModel = None

        self._central_layout = QVBoxLayout()
        self._central_layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(self._central_layout)

        self._filter_tag_view = FilterTagView()
        self._filter_tag_view.setVisible(False)
        self._filter_tag_view.add.connect(lambda: self._filter_tag_view.setVisible(True))
        self._filter_tag_view.empty.connect(lambda: self._filter_tag_view.setVisible(False))
        self._central_layout.addWidget(self._filter_tag_view)

        self._table_view = DataFrameTableView()
        self._table_view.horizontalHeader().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._table_view.horizontalHeader().customContextMenuRequested.connect(self._on_header_context_menu)
        self._table_view.customContextMenuRequested.connect(self._on_data_context_menu)
        self._central_layout.addWidget(self._table_view, 1)

    @property
    def data(self) -> pd.DataFrame:
        """
        Get the data in the table.
        """
        return self._table_model.df if self._table_model is not None else None

    @data.setter
    def data(self, value: pd.DataFrame):
        self._table_model = DataFrameTableModel(value)
        self._table_model.begin_transform.connect(self._on_table_model_begin_transform)
        self._table_model.end_transform.connect(self._on_table_model_end_transform)
        self._table_model.end_filtering.connect(self._on_table_model_end_filtering)
        self._refresh()

    def get_selected_value(self) -> str:
        """
        Get the selected value in the table.
        """
        if self._table_view.selectedIndexes():
            selected_index = self._table_view.selectedIndexes()[0]
            return self._table_model.data(selected_index, Qt.ItemDataRole.DisplayRole)

        return None

    def is_filtered(self) -> bool:
        """
        Check if the data is filtered.
        """
        if self._table_model is None:
            return False

        return len(self._table_model.filters) > 0

    def get_data_shape(self) -> Tuple[int, int]:
        """
        Get the shape of the original data.
        """
        if self._table_model is None or self._table_model.base_df is None:
            return None

        return self._table_model.base_df.shape

    def get_filtered_data_shape(self) -> Tuple[int, int]:
        """
        Get the shape of the filtered data.
        """
        if self._table_model is None or self._table_model.transformed_df is None:
            return None

        return self._table_model.transformed_df.shape

    def _refresh(self):
        self._table_view.setModel(self._table_model)

    def _add_filter(self, filter_: DataFrameFilter):
        """
        Add a filter to the table model.
        """
        filter_tag = FilterTag(filter_)
        filter_tag.close.connect(lambda: self._filter_tag_view.remove_tag(filter_tag))
        filter_tag.close.connect(lambda: self._remove_filter(filter_tag.filter))
        self._filter_tag_view.add_tag(filter_tag)

        self._table_model.add_filter(filter_)

    def _remove_filter(self, filter_: DataFrameFilter):
        """
        Remove a filter from the table model.
        """
        self._table_model.remove_filter(filter_)

    def _on_table_model_begin_transform(self):
        """
        Handle the table model beginning to transform.
        """
        self._filter_tag_view.setEnabled(False)
        self._table_view.setEnabled(False)
        self._table_view.loading = True

    def _on_table_model_end_transform(self):
        """
        Handle the table model ending to transform.
        """
        self._filter_tag_view.setEnabled(True)
        self._table_view.setEnabled(True)
        self._table_view.loading = False

    def _on_table_model_end_filtering(self):
        """
        Handle the table model ending to filter.
        """
        self.tableFiltered.emit()

    def _on_data_context_menu_copy(self, pos: QPoint):
        """
        Handle the context menu copy action.
        """
        selected_index = self._table_view.indexAt(pos)
        column_value = self._table_model.df.iloc[selected_index.row(), selected_index.column()]
        QApplication.clipboard().setText(str(column_value))

    def _on_data_context_menu_filter(self, pos: QPoint, operation: DataFrameFilterOperation):
        """
        Handle the context menu filter action.
        """
        selected_index = self._table_view.indexAt(pos)
        column_name = self._table_model.df.columns[selected_index.column()]
        column_value = self._table_model.df.iloc[selected_index.row(), selected_index.column()]

        self._add_filter(DataFrameFilter(column_name, operation, column_value))

    def _on_data_context_menu(self, pos: QPoint):
        """
        Handle the data context menu.
        """
        if not self._table_view.indexAt(pos).isValid():
            return

        menu = QMenu(self)

        copy_action = menu.addAction(self.tr("Copy"))
        copy_action.triggered.connect(lambda: self._on_data_context_menu_copy(pos))

        menu.addSeparator()

        filter_menu = menu.addMenu(self.tr("Filter"))

        filter_equal_action = filter_menu.addAction(self.tr("Equal"))
        filter_equal_action.triggered.connect(
            lambda: self._on_data_context_menu_filter(pos, DataFrameFilterOperation.EQUAL))

        filter_not_equal_action = filter_menu.addAction(self.tr("Not Equal"))
        filter_not_equal_action.triggered.connect(
            lambda: self._on_data_context_menu_filter(pos, DataFrameFilterOperation.NOT_EQUAL))

        filter_greater_action = filter_menu.addAction(self.tr("Greater Than"))
        filter_greater_action.triggered.connect(
            lambda: self._on_data_context_menu_filter(pos, DataFrameFilterOperation.GREATER_THAN))

        filter_greater_equal_action = filter_menu.addAction(self.tr("Greater Than or Equal"))
        filter_greater_equal_action.triggered.connect(
            lambda: self._on_data_context_menu_filter(pos, DataFrameFilterOperation.GREATER_THAN_OR_EQUAL))

        filter_less_action = filter_menu.addAction(self.tr("Less Than"))
        filter_less_action.triggered.connect(
            lambda: self._on_data_context_menu_filter(pos, DataFrameFilterOperation.LESS_THAN))

        filter_less_equal_action = filter_menu.addAction(self.tr("Less Than or Equal"))
        filter_less_equal_action.triggered.connect(
            lambda: self._on_data_context_menu_filter(pos, DataFrameFilterOperation.LESS_THAN_OR_EQUAL))

        menu.exec(self._table_view.mapToGlobal(pos))

    def _on_header_context_menu_copy_column_name(self, pos: QPoint):
        """
        Handle the header context menu copy column name action.
        """
        column_index = self._table_view.horizontalHeader().logicalIndexAt(pos)
        column_name = self._table_model.df.columns[column_index]
        QApplication.clipboard().setText(str(column_name))

    def _on_header_context_field_values(self, pos: QPoint):
        """
        Handle the header context menu field values action.
        """
        column_index = self._table_view.horizontalHeader().logicalIndexAt(pos)
        column_name = self._table_model.df.columns[column_index]

        value_counts = self._table_model.df[column_name].value_counts(dropna=False)
        field_values = pd.DataFrame(value_counts).reset_index()
        field_values.columns = [self.tr("Value"), self.tr("Count")]

        dialog = QvdFileFieldValuesDialog(column_name, field_values, self)
        dialog.filtered.connect(self._add_filter)
        dialog.exec()

    def _on_header_context_menu(self, pos: QPoint):
        """
        Handle the header context menu.
        """
        if self._table_view.horizontalHeader().logicalIndexAt(pos) == -1:
            return

        menu = QMenu(self)

        copy_column_name_action = menu.addAction(self.tr("Copy Column Name"))
        copy_column_name_action.triggered.connect(lambda: self._on_header_context_menu_copy_column_name(pos))

        field_values_action = menu.addAction(self.tr("Field Values"))
        field_values_action.triggered.connect(lambda: self._on_header_context_field_values(pos))

        menu.exec(self._table_view.horizontalHeader().mapToGlobal(pos))

class QvdFileErrorView(QWidget):
    """
    Widget that represents a QVD file error view.
    """
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self._error: Exception = None
        self._error_title: str = None
        self._error_message: str = None

        self._central_layout = QVBoxLayout()
        self._central_layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(self._central_layout)

        self._central_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self._error_icon_label = QLabel()
        self._error_icon_label.setAlignment(Qt.AlignCenter)
        self._error_icon_label.setPixmap(QIcon(":/icons/triangle-exclamation-amber-500.svg").pixmap(64, 64))
        self._central_layout.addWidget(self._error_icon_label)

        self._title_label = QLabel()
        self._title_label.setAlignment(Qt.AlignCenter)
        self._title_label.setStyleSheet("font-size: 18px;")
        self._central_layout.addWidget(self._title_label)

        self._message_label = QLabel()
        self._message_label.setAlignment(Qt.AlignCenter)
        self._central_layout.addWidget(self._message_label)

        self._central_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

    @property
    def error(self) -> Exception:
        """
        Get the error that occurred while loading the file.
        """
        return self._error

    @error.setter
    def error(self, value: Exception):
        self._error = value

        if isinstance(value, FileNotFoundError):
            self._error_title = "File Not Found"
            self._error_message = "The specified file has been moved or doesn't longer exist."
        else:
            self._error_title = "Unexpected Error"
            self._error_message = "Reading the file failed; the file may be corrupted."

        self._refresh()

    def _refresh(self):
        self._title_label.setText(self._error_title)
        self._message_label.setText(self._error_message)

class QvdFileLoadingView(QWidget):
    """
    Widget that represents a QVD file loading view.
    """
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self._central_layout = QVBoxLayout()
        self._central_layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(self._central_layout)

        self._spinner = Spinner()
        self._spinner.setFixedHeight(32)
        self._central_layout.addWidget(self._spinner)

        self._central_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

class QvdFileWidget(QStackedWidget):
    """
    QVD file widget, for displaying QVD files.
    """
    tableLoading = Signal()
    tableLoaded = Signal()
    tableErrored = Signal()
    tableFiltered = Signal()

    def __init__(self, path: str, parent: QWidget = None):
        super().__init__(parent)

        self._path = path
        self._loading: bool = False
        self._error: Exception = None
        self._data: pd.DataFrame = None

        self._data_view = QvdFileDataView()
        self._data_view.tableFiltered.connect(self.tableFiltered)
        self.addWidget(self._data_view)

        self._error_view = QvdFileErrorView()
        self.addWidget(self._error_view)

        self._loading_view = QvdFileLoadingView()
        self.addWidget(self._loading_view)

        self._load_qvd_file()

    @property
    def path(self) -> str:
        """
        Get the path of the QVD file.
        """
        return self._path

    @property
    def loading(self) -> bool:
        """
        Check if the file is still loading.
        """
        return self._loading

    @property
    def loaded(self) -> bool:
        """
        Check if the file has finished loading.
        """
        return not self._loading and self._error is None

    @property
    def errored(self) -> bool:
        """
        Check if an error occurred while loading the file.
        """
        return not self._loading and self._error is not None

    @property
    def error(self) -> Exception:
        """
        Get the error that occurred while loading the file.
        """
        return self._error

    @property
    def data(self) -> pd.DataFrame:
        """
        Get the data from the QVD file.
        """
        return self._data

    def is_filtered(self) -> bool:
        """
        Check if the data is filtered.
        """
        return self._data_view.is_filtered()

    def get_selected_value(self) -> str:
        """
        Get the selected value in the table.
        """
        return self._data_view.get_selected_value()

    def get_table_shape(self) -> Tuple[int, int]:
        """
        Get the shape of the table.
        """
        return self._data_view.get_data_shape()

    def get_filtered_table_shape(self) -> Tuple[int, int]:
        """
        Get the shape of the filtered table.
        """
        return self._data_view.get_filtered_data_shape()

    def _refresh(self):
        """
        Refresh the widget.
        """
        if self._loading:
            self.setCurrentWidget(self._loading_view)

            self.tableLoading.emit()
        elif self._error is not None:
            self._error_view.error = self._error
            self.setCurrentWidget(self._error_view)

            self.tableErrored.emit()
        else:
            self._data_view.data = self._data
            self.setCurrentWidget(self._data_view)

            self.tableLoaded.emit()

    def _on_task_data(self, data: pd.DataFrame):
        """
        Handle the task data.
        """
        self._data = data

    def _on_task_error(self, error: Tuple[Exception, type, str]):
        """
        Handle the task error.
        """
        self._error = error[0]

    def _on_task_finished(self):
        """
        Handle the task finishing.
        """
        self._loading = False
        self._refresh()

    def _load_qvd_file(self):
        """
        Load the QVD file.
        """
        self._loading = True
        self.setCurrentWidget(self._loading_view)

        task = LoadQvdFileTask(self._path)
        task.signals.data.connect(self._on_task_data)
        task.signals.error.connect(self._on_task_error)
        task.signals.finished.connect(self._on_task_finished)

        QThreadPool.globalInstance().start(task)
