"""
Module for loading QVD files in parallel.
"""

import sys
import traceback
from PySide6.QtCore import QRunnable, Signal, QObject
from pyqvd import QvdDataFrame
import pandas as pd

class LoadQvdFileTaskSignals(QObject):
    """
    Signals for the LoadQvdFileTask class.
    """
    finished = Signal()
    error = Signal(Exception)
    data = Signal(pd.DataFrame)

class LoadQvdFileTask(QRunnable):
    """
    Task for loading a QVD file.
    """
    def __init__(self, path: str):
        super().__init__()

        self.signals = LoadQvdFileTaskSignals()
        self._path = path

    def run(self) -> None:
        try:
            df = QvdDataFrame.from_qvd(self._path)
            df = df.to_pandas()

            self.signals.data.emit(df)
        # pylint: disable-next=bare-except
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((value, exctype, traceback.format_exc()))
        finally:
            self.signals.finished.emit()

class PersistQvdFileTaskSignals(QObject):
    """
    Signals for the PersistQvdFileTask class.
    """
    finished = Signal()
    succeeded = Signal()
    error = Signal(Exception)

class PersistQvdFileTask(QRunnable):
    """
    Task for persisting a QVD file.
    """
    def __init__(self, df: pd.DataFrame, path: str):
        super().__init__()

        self.signals = PersistQvdFileTaskSignals()
        self._df = df
        self._path = path

    def run(self) -> None:
        try:
            qvd = QvdDataFrame.from_pandas(self._df)
            qvd.to_qvd(self._path)

            self.signals.succeeded.emit()
        # pylint: disable-next=bare-except
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((value, exctype, traceback.format_exc()))
        finally:
            self.signals.finished.emit()

class ExportCsvFileTaskSignals(QObject):
    """
    Signals for the ExportCsvFileTask class.
    """
    finished = Signal()
    succeeded = Signal()
    error = Signal(Exception)

class ExportCsvFileTask(QRunnable):
    """
    Task for persisting a QVD file.
    """
    def __init__(self, df: pd.DataFrame, path: str):
        super().__init__()

        self.signals = ExportCsvFileTaskSignals()
        self._df = df
        self._path = path

    def run(self) -> None:
        try:
            self._df.to_csv(self._path, index=False)

            self.signals.succeeded.emit()
        # pylint: disable-next=bare-except
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((value, exctype, traceback.format_exc()))
        finally:
            self.signals.finished.emit()
