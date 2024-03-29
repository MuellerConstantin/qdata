"""
Contains widgets for displaying QVD files.
"""

from typing import Tuple
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSpacerItem, QSizePolicy, QLabel, QStyle, QTableView, QFrame
from PySide6.QtCore import QThreadPool, Qt
import pandas as pd
from qdata.widgets.progress import Spinner
from qdata.core.models import DataFrameTableModel
from qdata.parallel.qvd import LoadQvdFileTask

class QvdFileDataView(QWidget):
    """
    Widget that represents a QVD file data view.
    """
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self._table_model: DataFrameTableModel = None

        self._central_layout = QVBoxLayout()
        self.setLayout(self._central_layout)

        self._table_view = QTableView()
        self._table_view.setSortingEnabled(False)
        self._table_view.setStyleSheet("QTableView {border: 1px solid #d4d4d4;}")
        self._table_view.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Raised)
        self._table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectItems)
        self._table_view.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self._table_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._central_layout.addWidget(self._table_view, 2)

    @property
    def data(self) -> pd.DataFrame:
        """
        Get the data in the table.
        """
        return self._table_model.df if self._table_model is not None else None

    @data.setter
    def data(self, value: pd.DataFrame):
        if self._table_model is None:
            self._table_model = DataFrameTableModel(value)
        else:
            self._table_model.df = value

        self._refresh()

    def get_selected_value(self) -> str:
        """
        Get the selected value in the table.
        """
        if self._table_view.selectedIndexes():
            selected_index = self._table_view.selectedIndexes()[0]
            return self._table_model.data(selected_index, Qt.ItemDataRole.DisplayRole)

        return None

    def _refresh(self):
        self._table_view.setModel(self._table_model)

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
        self.setLayout(self._central_layout)

        self._central_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self._error_icon_label = QLabel()
        self._error_icon_label.setAlignment(Qt.AlignCenter)
        self._error_icon_label.setPixmap(self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxCritical)
                                         .pixmap(64, 64))
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
        self.setLayout(self._central_layout)

        self._spinner = Spinner()
        self._spinner.setFixedHeight(32)
        self._central_layout.addWidget(self._spinner)

        self._central_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

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

        self._central_layout = QVBoxLayout()
        self.setLayout(self._central_layout)

        self._loading_view = QvdFileLoadingView()
        self._loading_view.setVisible(True)
        self._central_layout.addWidget(self._loading_view)

        self._error_view = QvdFileErrorView()
        self._error_view.setVisible(False)
        self._central_layout.addWidget(self._error_view)

        self._data_view = QvdFileDataView()
        self._data_view.setVisible(False)
        self._central_layout.addWidget(self._data_view)

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

    def get_selected_value(self) -> str:
        """
        Get the selected value in the table.
        """
        return self._data_view.get_selected_value()

    def _refresh(self):
        """
        Refresh the widget.
        """
        if self._loading:
            self._loading_view.setVisible(True)
            self._error_view.setVisible(False)
            self._data_view.setVisible(False)
        elif self._error is not None:
            self._loading_view.setVisible(False)
            self._error_view.setVisible(True)
            self._data_view.setVisible(False)

            self._error_view.error = self._error
        else:
            self._loading_view.setVisible(False)
            self._error_view.setVisible(False)
            self._data_view.setVisible(True)

            self._data_view.data = self._data

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
