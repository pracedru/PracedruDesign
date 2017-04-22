from PyQt5.QtCore import QAbstractItemModel
from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import Qt

from Data.Document import Document
from GUI.Icons import get_icon

branches = ["Global Parameters", "Geometries", "Analyses", "Drawings", "Reports"]

class DocumentItemModel(QAbstractItemModel):
    def __init__(self, document: Document):
        QAbstractItemModel.__init__(self)
        self._doc = document
        if document is not None:
            document.add_change_handler(self.on_document_changed)

    def parent(self, index: QModelIndex=None):
        if not index.isValid():
            return QModelIndex()
        pntr = index.internalPointer()
        parent_row = 0
        if pntr is None:
            return QModelIndex()
        elif pntr in branches:
            return QModelIndex()

    def index(self, row, col, parent: QModelIndex=None, *args, **kwargs):
        if parent is None:
            return QModelIndex()
        if parent.internalPointer() is None:
            return self.createIndex(row, col, branches[row])
        return QModelIndex()

    def columnCount(self, parent=None, *args, **kwargs):
        return 1

    def rowCount(self, parent=None, *args, **kwargs):
        if parent is None:
            return 1
        if parent.internalPointer() is None:
            return len(branches)
        if parent.internalPointer() in branches:
            return 0

    def data(self, index: QModelIndex, role=None):
        col = index.column()
        row = index.row()
        data = None
        pntr = index.internalPointer()
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return pntr
        elif role == Qt.DecorationRole:
            if pntr in branches:
                return get_icon("default")
        return None

    def setData(self, index: QModelIndex, Any, role=None):
        pass

    def headerData(self, p_int, qt_orientation, role=None):
        if role == Qt.DisplayRole:
            if qt_orientation == Qt.Vertical:
                return p_int
            else:
                return "Name"

    def flags(self, index: QModelIndex):
        col = index.column()
        row = index.row()
        pntr = index.internalPointer()
        default_flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled

        return default_flags

    def on_document_changed(self, event):
        self.layoutChanged.emit()
