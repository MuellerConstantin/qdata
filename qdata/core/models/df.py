"""
Contains the models for handling tabular data.
"""

from typing import List, Tuple
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Signal, QThreadPool
from PySide6.QtGui import QFont
from pandas.api.types import is_datetime64_any_dtype as is_datetime
import pandas as pd
import numpy as np
from qdata.core.models.transform import DataFrameFilter
from qdata.parallel.df import FilterDataFrameTask, SortDataFrameTask

class DataFrameTableModelOptions:
    """
    Options for the DataFrameTableModel.
    """
    def __init__(self, float_format: str = "{:.4f}", int_format: str = "{:d}",
                 datetime_format: str = "%Y-%m-%d %H:%M:%S"):
        self._float_format = float_format
        self._int_format = int_format
        self._datetime_format = datetime_format

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
    def datetime_format(self) -> str:
        """
        Get the datetime format string.
        """
        return self._datetime_format

class DataFrameTableModel(QAbstractTableModel):
    """
    Custom table model for displaying a pandas DataFrame.
    """
    begin_transform = Signal()
    end_transform = Signal()
    begin_filtering = Signal()
    end_filtering = Signal()
    begin_sorting = Signal()
    end_sorting = Signal()

    def __init__(self, base_df: pd.DataFrame = None,
                 options: DataFrameTableModelOptions = DataFrameTableModelOptions()):
        super().__init__()

        self._options: DataFrameTableModelOptions = options
        self._base_df: pd.DataFrame = base_df
        self._transformed_df: pd.DataFrame = None
        self._filters: List[DataFrameFilter] = []
        self._transforming: bool = False

    def rowCount(self, parent: QModelIndex = ...) -> int:
        if parent.isValid() or self.df is None:
            return 0

        return self.df.shape[0]

    def columnCount(self, parent: QModelIndex = ...) -> int:
        if parent.isValid() or self.df is None:
            return 0

        return self.df.shape[1]

    # pylint: disable-next=unused-argument
    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled

    def data(self, index: QModelIndex, role: int = ...) -> object:
        if index.isValid() and self.df is not None:
            value = self.df.iloc[index.row(), index.column()]

            if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
                return self._format_data_value(value)
            elif role == Qt.ItemDataRole.UserRole:
                return value
            elif role == Qt.ItemDataRole.FontRole:
                if value is None:
                    font = QFont()
                    font.setItalic(True)

                    return font

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> object:
        if self.df is not None:
            if role == Qt.ItemDataRole.DisplayRole:
                if orientation == Qt.Orientation.Horizontal:
                    return self._format_header_value(self.df.columns[section])
                elif orientation == Qt.Orientation.Vertical:
                    return self._format_header_value(self.df.index[section])
            elif role == Qt.ItemDataRole.UserRole:
                if orientation == Qt.Orientation.Horizontal:
                    return self.df.columns[section]
                elif orientation == Qt.Orientation.Vertical:
                    return self.df.index[section]

        return None

    def sort(self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder):
        if self.df is None:
            return

        self._transforming = True
        self.begin_transform.emit()
        self.begin_sorting.emit()
        self.beginResetModel()

        copy_df = self.df.copy()
        column = copy_df.columns[column]

        task = SortDataFrameTask(copy_df, column, order == Qt.SortOrder.AscendingOrder)
        task.signals.data.connect(self._on_sort_task_data)
        task.signals.error.connect(self._on_sort_task_error)
        task.signals.finished.connect(self._on_sort_task_finished)

        QThreadPool.globalInstance().start(task)

    @property
    def base_df(self) -> pd.DataFrame:
        """
        Get the DataFrame.
        """
        return self._base_df

    @property
    def transformed_df(self) -> pd.DataFrame:
        """
        Get the transformed DataFrame.
        """
        return self._transformed_df

    @property
    def df(self) -> pd.DataFrame:
        """
        Get the DataFrame.
        """
        return self._transformed_df if self._transformed_df is not None else self._base_df

    @property
    def filters(self) -> List[DataFrameFilter]:
        """
        Get the filters.
        """
        return self._filters

    @property
    def transforming(self) -> bool:
        """
        Get whether the model is transforming.
        """
        return self._transforming

    @property
    def options(self) -> DataFrameTableModelOptions:
        """
        Get the options.
        """
        return self._options

    def add_filter(self, filter_: DataFrameFilter):
        """
        Add a filter to the DataFrame.
        """
        self._filters.append(filter_)
        self._apply_filters()

    def remove_filter(self, filter_: DataFrameFilter):
        """
        Remove a filter from the DataFrame.
        """
        self._filters.remove(filter_)
        self._apply_filters()

    def _format_data_value(self, value: object) -> str:
        """
        Format a data value for display.
        """
        if value is None:
            return "N/A"

        if is_datetime(type(value)):
            return value.strftime(self._options.datetime_format)

        if isinstance(value, str):
            if type(value) in [float, np.float64] and np.isnan(value):
                return ""
            if type(value) in [float, np.float64]:
                return self._options.float_format.format(value)
            if type(value) in [int, np.int64]:
                return self._options.int_format.format(value)

        return str(value)

    def _format_header_value(self, value: object) -> str:
        """
        Format a header value for display.
        """
        if isinstance(value, pd.DatetimeIndex):
            if value is not pd.NaT:
                return value.strftime(self._options.datetime_format)

        return str(value)

    def _apply_filters(self):
        """
        Apply the filters to the DataFrame.
        """
        if self._base_df is None:
            return

        self._transforming = True
        self.begin_transform.emit()
        self.begin_filtering.emit()
        self.beginResetModel()

        copy_df = self._base_df.copy()

        task = FilterDataFrameTask(copy_df, self._filters)
        task.signals.data.connect(self._on_filter_task_data)
        task.signals.error.connect(self._on_filter_task_error)
        task.signals.finished.connect(self._on_filter_task_finished)

        QThreadPool.globalInstance().start(task)

    def _on_filter_task_data(self, data: pd.DataFrame):
        """
        Handle the task data.
        """
        self._transformed_df = data


    def _on_filter_task_error(self, error: Tuple[Exception, type, str]):
        """
        Handle the task error.
        """
        raise error[0]

    def _on_filter_task_finished(self):
        """
        Handle the task finishing.
        """
        self._transforming = False
        self.end_transform.emit()
        self.end_filtering.emit()
        self.endResetModel()

    def _on_sort_task_data(self, data: pd.DataFrame):
        """
        Handle the task data.
        """
        self._transformed_df = data


    def _on_sort_task_error(self, error: Exception):
        """
        Handle the task error.
        """
        raise error

    def _on_sort_task_finished(self):
        """
        Handle the task finishing.
        """
        self._transforming = False
        self.end_transform.emit()
        self.end_sorting.emit()
        self.endResetModel()
