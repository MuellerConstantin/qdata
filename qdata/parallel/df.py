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
    Task for loading a QVD file.
    """
    def __init__(self, df: pd.DataFrame, filters: List[DataFrameFilter]):
        super().__init__()

        self.signals = FilterDataFrameTaskSignals()
        self._df = df
        self._filters = filters

    def run(self) -> None:
        try:
            for filter_ in self._filters:
                column_types = self._df[filter_.column].apply(type).unique()

                # Check if the column has multiple types
                if len(column_types) > 1:
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

            self.signals.data.emit(self._df)
        # pylint: disable-next=bare-except
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((value, exctype, traceback.format_exc()))
        finally:
            self.signals.finished.emit()
