"""
Module contains logic for working with DataFrames in parallel.
"""

import sys
import traceback
from typing import List
from PySide6.QtCore import QRunnable, Signal, QObject
import pandas as pd
from qdata.core.models.transform import DataFrameFilter, DataFrameFilterOperation

class FilterDataFrameTaskSignals(QObject):
    """
    Signals for the FilterDataFrameTask class.
    """
    finished = Signal()
    error = Signal(Exception)
    data = Signal(pd.DataFrame)

class FilterDataFrameTask(QRunnable):
    """
    Task for filtering a QVD file.
    """
    def __init__(self, df: pd.DataFrame, filters: List[DataFrameFilter]):
        super().__init__()

        self.signals = FilterDataFrameTaskSignals()
        self._df = df
        self._filters = filters

    def run(self) -> None:
        try:
            for filter_ in self._filters:
                # Separate handling when filtering for equality with None (missing values)
                if (filter_.value is None and (filter_.operation == DataFrameFilterOperation.EQUAL or
                                              filter_.operation == DataFrameFilterOperation.NOT_EQUAL)):
                    if filter_.operation == DataFrameFilterOperation.EQUAL:
                        self._df = self._df[self._df[filter_.column].isnull()]
                    elif filter_.operation == DataFrameFilterOperation.NOT_EQUAL:
                        self._df = self._df[self._df[filter_.column].notnull()]

                    continue

                column_types = self._df[filter_.column].apply(type).unique()
                column_types = [_type for _type in column_types if _type != type(None)]

                # Handle values as strings if multiple types are present or operation is string-based
                if (len(column_types) > 1) or (filter_.operation in [DataFrameFilterOperation.BEGINS_WITH,
                                                                     DataFrameFilterOperation.ENDS_WITH]):
                    column_values = self._df[filter_.column].astype(str)
                    compare_value = str(filter_.value)
                else:
                    column_values = self._df[filter_.column]
                    compare_value = filter_.value

                if filter_.operation == DataFrameFilterOperation.EQUAL:
                    self._df = self._df[column_values == compare_value]
                elif filter_.operation == DataFrameFilterOperation.NOT_EQUAL:
                    self._df = self._df[column_values != compare_value]
                elif filter_.operation == DataFrameFilterOperation.GREATER_THAN:
                    self._df = self._df[column_values > compare_value]
                elif filter_.operation == DataFrameFilterOperation.GREATER_THAN_OR_EQUAL:
                    self._df = self._df[column_values >= compare_value]
                elif filter_.operation == DataFrameFilterOperation.LESS_THAN:
                    self._df = self._df[column_values < compare_value]
                elif filter_.operation == DataFrameFilterOperation.LESS_THAN_OR_EQUAL:
                    self._df = self._df[column_values <= compare_value]
                elif filter_.operation == DataFrameFilterOperation.BEGINS_WITH:
                    self._df = self._df[column_values.str.startswith(compare_value)]
                elif filter_.operation == DataFrameFilterOperation.ENDS_WITH:
                    self._df = self._df[column_values.str.endswith(compare_value)]

            self.signals.data.emit(self._df)
        # pylint: disable-next=bare-except
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((value, exctype, traceback.format_exc()))
        finally:
            self.signals.finished.emit()

class SortDataFrameTaskSignals(QObject):
    """
    Signals for the SortDataFrameTask class.
    """
    finished = Signal()
    error = Signal(Exception)
    data = Signal(pd.DataFrame)

class SortDataFrameTask(QRunnable):
    """
    Task for sorting a QVD file.
    """
    def __init__(self, df: pd.DataFrame, column: str, ascending: bool):
        super().__init__()

        self.signals = SortDataFrameTaskSignals()
        self._df = df
        self._column = column
        self._ascending = ascending

    def run(self) -> None:
        try:
            column_types = self._df[self._column].apply(type).unique()

            # Check if the column has multiple types
            if len(column_types) > 1:
                column_values = self._df[self._column].astype(str)
            else:
                column_values = self._df[self._column]

            column_values = column_values.sort_values(ascending=self._ascending)
            self._df = self._df.reindex(column_values.index)

            self.signals.data.emit(self._df)
        # pylint: disable-next=bare-except
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((value, exctype, traceback.format_exc()))
        finally:
            self.signals.finished.emit()
