"""
Module for loading QVD files in parallel.
"""

import sys
import traceback
from PySide6.QtCore import QRunnable, Signal, QObject
from pyqvd import QvdTable
import pandas as pd

class LoadQvdFileTaskSignals(QObject):
    """
    Signals for the LoadQvdFileTask class.
    """
    finished = Signal()
    error = Signal(Exception)
    data = Signal(pd.DataFrame)
    progress = Signal(float)

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
            df = QvdTable([], [])

            itr = QvdTable.from_qvd(self._path, chunk_size=1000)
            nth_chunk = 0
            total_chunks = len(itr)

            for chunk in itr:
                df.concat(chunk, inplace=True)
                self.signals.progress.emit((nth_chunk / total_chunks) * 100)
                nth_chunk += 1

            df = df.to_pandas()

            self.signals.data.emit(df)
        # pylint: disable-next=bare-except
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((value, exctype, traceback.format_exc()))
        finally:
            self.signals.finished.emit()

class ImportCsvFileTaskSignals(QObject):
    """
    Signals for the ImportCsvFileTask class.
    """
    finished = Signal()
    error = Signal(Exception)
    data = Signal(pd.DataFrame)

class ImportCsvFileTask(QRunnable):
    """
    Task for loading a QVD file.
    """
    def __init__(self, path: str):
        super().__init__()

        self.signals = ImportCsvFileTaskSignals()
        self._path = path

    def run(self) -> None:
        try:
            df = pd.read_csv(self._path, keep_default_na=False, na_values=[''])
            df = df.where(df.notnull(), None)

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
            qvd = QvdTable.from_pandas(self._df)
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
