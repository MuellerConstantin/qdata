"""
Module contains the data frame widgets.
"""

from PySide6.QtWidgets import QTableView, QWidget, QFrame
from PySide6.QtGui import QResizeEvent, QPaintEvent, QPainter, QColor, QUndoStack, QUndoCommand
from PySide6.QtCore import Qt, Signal
from qdata.widgets.progress import Spinner
from qdata.core.models.df import DataFrameTableModel

class LoadingOverlay(QWidget):
    """
    Loading overlay widget.
    """
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self._spinner = Spinner(self)
        self._spinner.setFixedHeight(32)
        self._spinner.adjustSize()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)

        size = self.size()
        self._spinner.move(int(size.width() / 2 - self._spinner.width() / 2), 10)

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)

        size = self.size()
        painter = QPainter()

        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setBrush(QColor(30, 30, 30, 75))
        painter.drawRect(0, 0, size.width(), size.height())
        painter.end()

class DataFrameEditCommand(QUndoCommand):
    """
    Command for editing a data frame.
    """
    def __init__(self, model: DataFrameTableModel, row: int, col: int, old_value: object, new_value: object):
        super().__init__()

        self._model = model
        self._row = row
        self._col = col
        self._old_value = old_value
        self._new_value = new_value

    def undo(self):
        self._model.setData(self._model.index(self._row, self._col), self._old_value, Qt.ItemDataRole.UserRole)

    def redo(self):
        self._model.setData(self._model.index(self._row, self._col), self._new_value, Qt.ItemDataRole.UserRole)

class DataFrameTableView(QTableView):
    """
    Pandas data frame optimized table view.
    """
    table_unsaved_changes = Signal(bool)
    table_undoable = Signal(bool)
    table_redoable = Signal(bool)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.setSortingEnabled(True)
        self.setStyleSheet("QTableView {border: 1px solid #d4d4d4;}")
        self.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Raised)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectItems)
        self.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        self._undo_stack = QUndoStack(self)
        self._undo_stack.canUndoChanged.connect(self.table_undoable)
        self._undo_stack.canRedoChanged.connect(self.table_redoable)
        self._undo_stack.cleanChanged.connect(lambda clean: self.table_unsaved_changes.emit(not clean))

        self._loading = False

        self._loading_overlay = LoadingOverlay(self)
        self._loading_overlay.move(0, 0)
        self._loading_overlay.resize(self.width(), self.height())
        self._loading_overlay.hide()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)

        self._loading_overlay.move(0, 0)
        self._loading_overlay.resize(self.width(), self.height())

    @property
    def loading(self) -> bool:
        """
        Get the loading state.
        """
        return self._loading

    @loading.setter
    def loading(self, value: bool) -> None:
        """
        Set the loading state.
        """
        self._loading = value

        if self._loading:
            self._loading_overlay.show()
            self._loading_overlay.setEnabled(True)
        else:
            self._loading_overlay.hide()
            self._loading_overlay.setEnabled(False)

    @property
    def undoable(self) -> bool:
        """
        Get the undoable state.
        """
        return self._undo_stack.canUndo()

    @property
    def redoable(self) -> bool:
        """
        Get the redoable state.
        """
        return self._undo_stack.canRedo()

    @property
    def unsaved_changes(self) -> bool:
        """
        Get the unsaved changes state.
        """
        return not self._undo_stack.isClean()

    def setModel(self, model: DataFrameTableModel) -> None:
        super().setModel(model)

        if model is not None:
            model.data_edited.connect(self._on_data_edit)

    def undo(self) -> None:
        """
        Undo the last action.
        """
        self._undo_stack.undo()

    def redo(self) -> None:
        """
        Redo the last action.
        """
        self._undo_stack.redo()

    def mark_saved(self) -> None:
        """
        Mark the current state as saved.
        """
        self._undo_stack.setClean()

    def _on_data_edit(self, row: int, col: int, old_value: object, new_value: object) -> None:
        self._undo_stack.push(DataFrameEditCommand(self.model(), row, col, old_value, new_value))
