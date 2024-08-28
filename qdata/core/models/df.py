"""
Contains the models for handling tabular data.
"""

from typing import List, Tuple, Dict
from enum import Enum
import datetime as dt
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Signal, QThreadPool, QAbstractProxyModel
from PySide6.QtGui import QFont
from pandas.api.types import is_integer_dtype, is_float_dtype, is_datetime64_any_dtype
import pandas as pd
import numpy as np
from qdata.core.models.transform import DataFrameFilter
from qdata.parallel.df import FilterDataFrameTask, SortDataFrameTask

class DataFrameItemDataRole(Enum):
    """
    Custom item data roles for the DataFrameTableModel.
    """
    DATA_ROLE = Qt.ItemDataRole.UserRole + 1
    DATA_ROW_ROLE = Qt.ItemDataRole.UserRole + 2

class DataFrameTableModelOptions:
    """
    Options for the DataFrameTableModel.
    """
    def __init__(self, float_format: str = "{:.4f}", int_format: str = "{:d}",
                 date_format: str = "%Y-%m-%d",
                 time_format: str = "%H:%M:%S",
                 timedelta_format: str = "%H:%M:%S",
                 datetime_format: str = "%Y-%m-%d %H:%M:%S"):
        self._float_format = float_format
        self._int_format = int_format
        self._datetime_format = datetime_format
        self._date_format = date_format
        self._time_format = time_format
        self._timedelta_format = timedelta_format

    @property
    def float_format(self) -> str:
        """
        Get the float format string.
        """
        return self._float_format

    @property
    def int_format(self) -> str:
        """
        Get the int format string.
        """
        return self._int_format

    @property
    def date_format(self) -> str:
        """
        Get the date format string.
        """
        return self._date_format

    @property
    def time_format(self) -> str:
        """
        Get the time format string.
        """
        return self._time_format

    @property
    def datetime_format(self) -> str:
        """
        Get the datetime format string.
        """
        return self._datetime_format

class DataFrameTableModel(QAbstractTableModel):
    """
    Custom table model for displaying a pandas DataFrame.
    """
    data_edited = Signal(int, int, object, object)

    def __init__(self, dataframe: pd.DataFrame = pd.DataFrame(),
                 options: DataFrameTableModelOptions = DataFrameTableModelOptions()):
        super().__init__()

        self._options: DataFrameTableModelOptions = options
        self._dataframe: pd.DataFrame = dataframe

    @property
    def options(self) -> DataFrameTableModelOptions:
        """
        Get the options.
        """
        return self._options

    @options.setter
    def options(self, options: DataFrameTableModelOptions):
        self.beginResetModel()
        self._options = options
        self.endResetModel()

    @property
    def dataframe(self):
        """
        Get the dataframe property.
        """
        return self._dataframe

    @dataframe.setter
    def dataframe(self, dataframe: pd.DataFrame):
        self.beginResetModel()
        self._dataframe = dataframe
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent != QModelIndex():
            return 0

        return len(self._dataframe)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent != QModelIndex():
            return 0

        return len(self._dataframe.columns)

    # pylint: disable-next=unused-argument
    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable

    def data(self, index: QModelIndex, role: int = ...) -> object:
        if index.isValid() and self._dataframe is not None:
            value = self._dataframe.iat[index.row(), index.column()]

            if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
                return self.format_data_value(value)
            elif role == DataFrameItemDataRole.DATA_ROLE:
                return value
            elif role == DataFrameItemDataRole.DATA_ROW_ROLE:
                return self._dataframe.iloc[index.row()]
            elif role == Qt.ItemDataRole.FontRole:
                if value is None or pd.isna(value) or (is_float_dtype(type(value)) and np.isnan(value)):
                    font = QFont()
                    font.setItalic(True)

                    return font

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> object:
        if self._dataframe is not None:
            if role == Qt.ItemDataRole.DisplayRole:
                if orientation == Qt.Orientation.Horizontal:
                    return self.format_header_value(self._dataframe.columns[section])
                elif orientation == Qt.Orientation.Vertical:
                    return self.format_header_value(self._dataframe.index[section])
            elif role == DataFrameItemDataRole.DATA_ROLE:
                if orientation == Qt.Orientation.Horizontal:
                    return self._dataframe.columns[section]
                elif orientation == Qt.Orientation.Vertical:
                    return self._dataframe.index[section]

        return None

    def setData(self, index: QModelIndex, value: object, role: int = ...) -> bool:
        if index.isValid() and self._dataframe is not None:
            if role == Qt.ItemDataRole.EditRole or role == DataFrameItemDataRole.DATA_ROLE:
                previous_value = self._dataframe.iat[index.row(), index.column()]

                if previous_value == value:
                    return False

                # Update the base DataFrame
                self._dataframe.iat[index.row(), index.column()] = value

                top_left = self.index(index.row(), index.column())
                bottom_right = self.index(index.row(), index.column())

                self.dataChanged.emit(top_left, bottom_right, [Qt.ItemDataRole.DisplayRole,
                                                               Qt.ItemDataRole.EditRole,
                                                               DataFrameItemDataRole.DATA_ROLE,
                                                               DataFrameItemDataRole.DATA_ROW_ROLE])

                return True
            elif role == DataFrameItemDataRole.DATA_ROW_ROLE:
                previous_row = self._dataframe.iloc[index.row()].copy()

                if previous_row.equals(value):
                    return False

                # Update the base DataFrame
                self._dataframe.iloc[index.row()] = value

                top_left = self.index(index.row(), 0)
                bottom_right = self.index(index.row(), self.columnCount() - 1)

                self.dataChanged.emit(top_left, bottom_right, [Qt.ItemDataRole.DisplayRole,
                                                               Qt.ItemDataRole.EditRole,
                                                               DataFrameItemDataRole.DATA_ROLE,
                                                               DataFrameItemDataRole.DATA_ROW_ROLE])

                return True

        return False

    def setHeaderData(self, section: int, orientation: Qt.Orientation, value: object, role: int = ...) -> bool:
        if self._dataframe is not None:
            if role == Qt.ItemDataRole.EditRole or role == DataFrameItemDataRole.DATA_ROLE:
                if orientation == Qt.Orientation.Horizontal:
                    previous_value = self._dataframe.columns[section]

                    if previous_value == value:
                        return False

                    self._dataframe.columns.values[section] = value

                    self.headerDataChanged.emit(orientation, section, section)

                    return True
                elif orientation == Qt.Orientation.Vertical:
                    previous_value = self._dataframe.index[section]

                    if previous_value == value:
                        return False

                    self._dataframe.index.values[section] = value

                    self.headerDataChanged.emit(orientation, section, section)

                    return True

        return False

    def insertRow(self, row: int, parent: QModelIndex = QModelIndex()) -> bool:
        if parent != QModelIndex():
            return False

        self.beginInsertRows(parent, row, row)

        empty_row = pd.Series([""] * len(self._dataframe.columns), index=self._dataframe.columns)

        dataframe_part1 = self._dataframe.iloc[:row]
        dataframe_part2 = self._dataframe.iloc[row:]

        self._dataframe = pd.concat([dataframe_part1, pd.DataFrame([empty_row]),
                                     dataframe_part2]).reset_index(drop=True)

        self.endInsertRows()

        return True

    def removeRow(self, row: int, parent: QModelIndex = QModelIndex()) -> bool:
        if parent != QModelIndex():
            return False

        self.beginRemoveRows(parent, row, row)

        self._dataframe = self._dataframe.drop(self._dataframe.index[row]).reset_index(drop=True)

        self.endRemoveRows()

        return True

    def format_data_value(self, value: object) -> str:
        """
        Format a data value for display.
        """
        if value is None or pd.isna(value):
            return "N/A"

        value_type = type(value)

        if is_integer_dtype(value_type):
            return self._options.int_format.format(value)
        if is_float_dtype(value_type):
            if np.isnan(value):
                return "NaN"

            return self._options.float_format.format(value)
        if isinstance(value, pd.Timestamp):
            return value.to_pydatetime().strftime(self._options.datetime_format)
        if is_datetime64_any_dtype(value_type):
            return value.to_pydatetime().strftime(self._options.datetime_format)
        if isinstance(value, pd.Timedelta):
            days = value.to_pytimedelta().days
            hours, seconds = divmod(value.to_pytimedelta().seconds, 60 * 60)
            minutes, seconds = divmod(seconds, 60)

            return f"{days} {hours:02}:{minutes:02}:{seconds:02}"
        if isinstance(value, dt.datetime):
            return value.strftime(self._options.datetime_format)
        if isinstance(value, dt.date):
            return value.strftime(self._options.date_format)
        if isinstance(value, dt.time):
            return value.strftime(self._options.time_format)
        if isinstance(value, dt.timedelta):
            days = value.days
            hours, seconds = divmod(value.seconds, 60 * 60)
            minutes, seconds = divmod(seconds, 60)

            return f"{days} {hours:02}:{minutes:02}:{seconds:02}"

        return str(value)

    def format_header_value(self, value: object) -> str:
        """
        Format a header value for display.
        """
        if isinstance(value, pd.DatetimeIndex):
            if value is not pd.NaT:
                return value.strftime(self._options.datetime_format)

        return str(value)

class DataFrameSortFilterProxyModel(QAbstractProxyModel):
    """
    Table filter proxy model class that filters a pandas DataFrame.
    """
    invalidated = Signal()
    begin_transform = Signal()
    end_transform = Signal()

    def __init__(self):
        super().__init__()

        self._source_model: DataFrameTableModel = None
        self._proxy_dataframe: pd.DataFrame = None
        self._source_to_proxy_mapping: Dict[int, int] = {}
        self._proxy_to_source_mapping: Dict[int, int] = {}
        self._filters: List[DataFrameFilter] = []

    @property
    def dataframe(self) -> pd.DataFrame:
        """
        Get the proxy dataframe.
        """
        return self._proxy_dataframe

    @property
    def filters(self) -> List[DataFrameFilter]:
        """
        Get the set filters.
        """
        return self._filters

    def setSourceModel(self, source_model: DataFrameTableModel):
        self.beginResetModel()

        if self._source_model is not None:
            self._source_model.dataChanged.disconnect(self._on_source_model_data_changed)
            self._source_model.headerDataChanged.disconnect(self._on_source_model_header_data_changed)
            self._source_model.layoutAboutToBeChanged.disconnect(self.layoutAboutToBeChanged.emit)
            self._source_model.layoutChanged.disconnect(self._on_source_model_layout_changed)
            self._source_model.modelAboutToBeReset.disconnect(self.modelAboutToBeReset.emit)
            self._source_model.modelReset.disconnect(self._on_source_model_model_reset)
            self._source_model.rowsAboutToBeInserted.disconnect(self.rowsAboutToBeInserted.emit)
            self._source_model.rowsInserted.disconnect(self._on_source_model_rows_inserted)
            self._source_model.rowsAboutToBeMoved.disconnect(self.rowsAboutToBeMoved.emit)
            self._source_model.rowsMoved.disconnect(self._on_source_model_rows_moved)
            self._source_model.rowsAboutToBeRemoved.disconnect(self.rowsAboutToBeRemoved.emit)
            self._source_model.rowsRemoved.disconnect(self._on_source_model_rows_removed)
            self._source_model.columnsAboutToBeInserted.disconnect(self.columnsAboutToBeInserted.emit)
            self._source_model.columnsInserted.disconnect(self._on_source_model_columns_inserted)
            self._source_model.columnsAboutToBeMoved.disconnect(self.columnsAboutToBeMoved.emit)
            self._source_model.columnsMoved.disconnect(self._on_source_model_columns_moved)
            self._source_model.columnsAboutToBeRemoved.disconnect(self.columnsAboutToBeRemoved.emit)
            self._source_model.columnsRemoved.disconnect(self._on_source_model_columns_removed)

        self._source_model = source_model
        self._proxy_dataframe = self._source_model.dataframe.copy()

        self._update_mapping()

        self._source_model.dataChanged.connect(self._on_source_model_data_changed)
        self._source_model.headerDataChanged.connect(self._on_source_model_header_data_changed)
        self._source_model.layoutAboutToBeChanged.connect(self.layoutAboutToBeChanged.emit)
        self._source_model.layoutChanged.connect(self._on_source_model_layout_changed)
        self._source_model.modelAboutToBeReset.connect(self.modelAboutToBeReset.emit)
        self._source_model.modelReset.connect(self._on_source_model_model_reset)
        self._source_model.rowsAboutToBeInserted.connect(self.rowsAboutToBeInserted.emit)
        self._source_model.rowsInserted.connect(self._on_source_model_rows_inserted)
        self._source_model.rowsAboutToBeMoved.connect(self.rowsAboutToBeMoved.emit)
        self._source_model.rowsMoved.connect(self._on_source_model_rows_moved)
        self._source_model.rowsAboutToBeRemoved.connect(self.rowsAboutToBeRemoved.emit)
        self._source_model.rowsRemoved.connect(self._on_source_model_rows_removed)
        self._source_model.columnsAboutToBeInserted.connect(self.columnsAboutToBeInserted.emit)
        self._source_model.columnsInserted.connect(self._on_source_model_columns_inserted)
        self._source_model.columnsAboutToBeMoved.connect(self.columnsAboutToBeMoved.emit)
        self._source_model.columnsMoved.connect(self._on_source_model_columns_moved)
        self._source_model.columnsAboutToBeRemoved.connect(self.columnsAboutToBeRemoved.emit)
        self._source_model.columnsRemoved.connect(self._on_source_model_columns_removed)

        self.endResetModel()

    def sourceModel(self) -> DataFrameTableModel:
        return self._source_model

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent != QModelIndex():
            return 0

        return len(self._proxy_dataframe)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent != QModelIndex():
            return 0

        return len(self._proxy_dataframe.columns)

    def data(self, index: QModelIndex, role: int = ...) -> object:
        if index.isValid() and self._proxy_dataframe is not None:
            value = self._proxy_dataframe.iat[index.row(), index.column()]

            if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
                return self._source_model.format_data_value(value)
            elif role == DataFrameItemDataRole.DATA_ROLE:
                return value
            elif role == DataFrameItemDataRole.DATA_ROW_ROLE:
                return self._proxy_dataframe.iloc[index.row()]
            elif role == Qt.ItemDataRole.FontRole:
                if value is None or pd.isna(value) or (is_float_dtype(type(value)) and np.isnan(value)):
                    font = QFont()
                    font.setItalic(True)

                    return font

        return None

    def setData(self, index: QModelIndex, value: object, role: int = ...) -> bool:
        source_index = self.mapToSource(index)

        if source_index.isValid():
            return self._source_model.setData(source_index, value, role)

        return False

    def setHeaderData(self, section: int, orientation: Qt.Orientation, value: object, role: int = ...) -> bool:
        return self._source_model.setHeaderData(section, orientation, value, role)

    def insertRow(self, row: int, parent: QModelIndex = QModelIndex()) -> bool:
        if parent != QModelIndex():
            return False

        source_row = self.mapToSource(self.index(row, 0)).row()

        return self._source_model.insertRow(source_row, parent)

    def removeRow(self, row: int, parent: QModelIndex = QModelIndex()) -> bool:
        if parent != QModelIndex():
            return False

        source_row = self.mapToSource(self.index(row, 0)).row()

        return self._source_model.removeRow(source_row, parent)

    def insertColumn(self, column: int, parent: QModelIndex = QModelIndex()) -> bool:
        if parent != QModelIndex():
            return False

        return self._source_model.insertColumn(column, parent)

    def removeColumn(self, column: int, parent: QModelIndex = QModelIndex()) -> bool:
        if parent != QModelIndex():
            return False

        return self._source_model.removeColumn(column, parent)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> object:
        if self._proxy_dataframe is not None:
            if role == Qt.ItemDataRole.DisplayRole:
                if orientation == Qt.Orientation.Horizontal:
                    return self._source_model.format_header_value(self._proxy_dataframe.columns[section])
                elif orientation == Qt.Orientation.Vertical:
                    return self._source_model.format_header_value(self._proxy_dataframe.index[section])
            elif role == DataFrameItemDataRole.DATA_ROLE:
                if orientation == Qt.Orientation.Horizontal:
                    return self._proxy_dataframe.columns[section]
                elif orientation == Qt.Orientation.Vertical:
                    return self._data_proxy_dataframeframe.index[section]

        return None

    # pylint: disable-next=unused-argument
    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable

    # pylint: disable-next=unused-argument
    def parent(self, index: QModelIndex) -> QModelIndex:
        return QModelIndex()

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        if parent != QModelIndex():
            return QModelIndex()

        return self.createIndex(row, column)

    def mapFromSource(self, source_index: QModelIndex) -> QModelIndex:
        if source_index.row() in self._source_to_proxy_mapping:
            return self.index(self._source_to_proxy_mapping[source_index.row()], source_index.column())

        return QModelIndex()

    def mapToSource(self, proxy_index: QModelIndex) -> QModelIndex:
        if proxy_index.row() in self._proxy_to_source_mapping:
            return self._source_model.index(self._proxy_to_source_mapping[proxy_index.row()], proxy_index.column())

        return QModelIndex()

    def sort(self, column: int, order: Qt.SortOrder = Qt.AscendingOrder):
        if self._source_model.dataframe is None:
            return

        self.layoutAboutToBeChanged.emit()
        self.begin_transform.emit()

        copy_df = (self._proxy_dataframe.copy() if self._proxy_dataframe is not None
                   else self._source_model.dataframe.copy())
        column = copy_df.columns[column]

        task = SortDataFrameTask(copy_df, column, order == Qt.SortOrder.AscendingOrder)
        task.signals.data.connect(self._on_sort_task_data)
        task.signals.error.connect(self._on_sort_task_error)
        task.signals.finished.connect(self._on_sort_task_finished)

        QThreadPool.globalInstance().start(task)

    def add_filter(self, filter_: DataFrameFilter):
        """
        Add a filter to the model.
        """
        self._filters.append(filter_)

        self._apply_filters()

    def remove_filter(self, filter_: DataFrameFilter):
        """
        Remove a filter from the model.
        """
        self._filters.remove(filter_)

        self._apply_filters()

    def clear_filters(self):
        """
        Clear all filters from the model.
        """
        self._filters.clear()

        self._apply_filters()

    def invalidate(self):
        """
        Invalidate the model.
        """
        self.clear_filters()
        self._proxy_dataframe = self._source_model.dataframe.copy()
        self._update_mapping()

        self.invalidated.emit()

    def _apply_filters(self):
        if self._source_model.dataframe is None:
            return

        self.beginResetModel()
        self.begin_transform.emit()

        copy_df = self._source_model.dataframe.copy()

        task = FilterDataFrameTask(copy_df, self._filters)
        task.signals.data.connect(self._on_filter_task_data)
        task.signals.error.connect(self._on_filter_task_error)
        task.signals.finished.connect(self._on_filter_task_finished)

        QThreadPool.globalInstance().start(task)

    def _update_mapping(self):
        self._source_to_proxy_mapping = {}
        self._proxy_to_source_mapping = {}

        if self._source_model is None:
            return

        for proxy_location_index, pandas_index in enumerate(self._proxy_dataframe.index):
            source_location_index = self._source_model.dataframe.index.get_loc(pandas_index)
            self._source_to_proxy_mapping[source_location_index] = proxy_location_index
            self._proxy_to_source_mapping[proxy_location_index] = source_location_index

    def _on_filter_task_data(self, data: pd.DataFrame):
        """
        Handle the task data.
        """
        self._proxy_dataframe = data

        self._update_mapping()

    def _on_filter_task_error(self, error: Tuple[Exception, type, str]):
        """
        Handle the task error.
        """
        raise error[0]

    def _on_filter_task_finished(self):
        """
        Handle the task finishing.
        """
        self.endResetModel()
        self.end_transform.emit()

    def _on_sort_task_data(self, data: pd.DataFrame):
        """
        Handle the task data.
        """
        self._proxy_dataframe = data

        self._update_mapping()

    def _on_sort_task_error(self, error: Exception):
        """
        Handle the task error.
        """
        raise error

    def _on_sort_task_finished(self):
        """
        Handle the task finishing.
        """
        self.layoutChanged.emit()
        self.end_transform.emit()

    def _on_source_model_data_changed(self, top_left: QModelIndex, bottom_right: QModelIndex, roles: List[int]):
        self.beginResetModel()

        self.invalidate()

        self.endResetModel()

    def _on_source_model_header_data_changed(self, orientation: Qt.Orientation, first: int, last: int):
        self.beginResetModel()

        self.invalidate()

        self.endResetModel()

    def _on_source_model_model_reset(self):
        self.beginResetModel()

        self.invalidate()

        self.endResetModel()

    def _on_source_model_layout_changed(self):
        self.beginResetModel()

        self.invalidate()

        self.endResetModel()

    def _on_source_model_rows_inserted(self, parent: QModelIndex, start: int, end: int):
        self.beginResetModel()

        self.invalidate()

        self.endResetModel()

    def _on_source_model_rows_removed(self, parent: QModelIndex, start: int, end: int):
        self.beginResetModel()

        self.invalidate()

        self.endResetModel()

    def _on_source_model_rows_moved(self, parent: QModelIndex, start: int, end: int,
                                    destination: QModelIndex, row: int):
        self.beginResetModel()

        self.invalidate()

        self.endResetModel()

    def _on_source_model_columns_inserted(self, parent: QModelIndex, start: int, end: int):
        self.beginResetModel()

        self.invalidate()

        self.endResetModel()

    def _on_source_model_columns_removed(self, parent: QModelIndex, start: int, end: int):
        self.beginResetModel()

        self.invalidate()

        self.endResetModel()

    def _on_source_model_columns_moved(self, parent: QModelIndex,
                                       start: int, end: int, destination: QModelIndex, column: int):
        self.beginResetModel()

        self.invalidate()

        self.endResetModel()
