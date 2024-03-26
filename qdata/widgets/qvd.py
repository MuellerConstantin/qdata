"""
Contains widgets for displaying QVD files.
"""

from typing import Tuple
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QThreadPool
import pandas as pd
from qdata.parallel.qvd import LoadQvdFileTask

class QvdFileWidget(QWidget):
    """
    QVD file widget, for displaying QVD files.
    """
    def __init__(self, path: str, parent: QWidget = None):
        super().__init__(parent)

        self._path = path
        self._loading: bool = True
        self._error: Exception = None
        self._data: pd.DataFrame = None

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
        return not self._loading

    @property
    def errored(self) -> bool:
        """
        Check if an error occurred while loading the file.
        """
        return self.loaded and self._error is not None

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

    def _refresh(self):
        """
        Refresh the widget.
        """

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
        task = LoadQvdFileTask(self._path)
        task.signals.data.connect(self._on_task_data)
        task.signals.error.connect(self._on_task_error)
        task.signals.finished.connect(self._on_task_finished)

        QThreadPool.globalInstance().start(task)
