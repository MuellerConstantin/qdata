"""
Module contains the Qt models for the QData application.
"""

from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from pandas.api.types import is_datetime64_any_dtype as is_datetime
import pandas as pd
import numpy as np

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
    def __init__(self, df: pd.DataFrame = None, options: DataFrameTableModelOptions = DataFrameTableModelOptions()):
        super().__init__()

        self._options: DataFrameTableModelOptions = options
        self._df: pd.DataFrame = df

    def rowCount(self, parent: QModelIndex = ...) -> int:
        if parent.isValid() or self._df is None:
            return 0

        return self._df.shape[0]

    def columnCount(self, parent: QModelIndex = ...) -> int:
        if parent.isValid() or self._df is None:
            return 0

        return self._df.shape[1]

    # pylint: disable-next=unused-argument
    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled

    def data(self, index: QModelIndex, role: int = ...) -> object:
        if index.isValid() and self._df is not None:
            value = self._df.iloc[index.row(), index.column()]

            if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
                return self._format_data_value(value)
            elif role == Qt.ItemDataRole.UserRole:
                return value

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> object:
        if self._df is not None:
            if role == Qt.ItemDataRole.DisplayRole:
                if orientation == Qt.Orientation.Horizontal:
                    return self._format_header_value(self._df.columns[section])
                elif orientation == Qt.Orientation.Vertical:
                    return self._format_header_value(self._df.index[section])
            elif role == Qt.ItemDataRole.UserRole:
                if orientation == Qt.Orientation.Horizontal:
                    return self._df.columns[section]
                elif orientation == Qt.Orientation.Vertical:
                    return self._df.index[section]

        return None

    @property
    def df(self) -> pd.DataFrame:
        """
        Get the DataFrame.
        """
        return self._df

    @df.setter
    def df(self, value: pd.DataFrame):
        self._df = value
        self.layoutChanged.emit()

    def _format_data_value(self, value: object) -> str:
        """
        Format a data value for display.
        """
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
