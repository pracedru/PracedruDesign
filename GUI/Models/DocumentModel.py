from PyQt5.QtCore import QAbstractItemModel
from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import QObject
from PyQt5.QtCore import Qt

from Data.Document import Document
from Data.Parameters import Parameters
from GUI.Icons import get_icon


class DocumentItemModel(QAbstractItemModel):
    def __init__(self, document: Document):
        QAbstractItemModel.__init__(self)
        self._doc = document
        self._root_item = DocumentModelItem(document, self)
        self.populate()
        if document is not None:
            document.add_change_handler(self.on_document_changed)

    def populate(self):
        DocumentModelItem(self._doc.get_parameters(), self, self._root_item)
        DocumentModelItem(None, self, self._root_item, "Geometries")
        DocumentModelItem(None, self, self._root_item, "Analyses")
        DocumentModelItem(None, self, self._root_item, "Drawings")
        DocumentModelItem(None, self, self._root_item, "Reports")

    def parent(self, index: QModelIndex=None):
        if not index.isValid():
            return QModelIndex()
        model_item = index.internalPointer()
        if model_item is None:
            return QModelIndex()
        elif model_item == self._root_item:
            return QModelIndex()
        else:
            row = model_item.parent().children().index(model_item)
            return self.createIndex(row, 0, model_item.parent())
        return QModelIndex()

    def index(self, row, col, parent: QModelIndex=None, *args, **kwargs):
        if parent is None:
            return self.createIndex(row, col, self._root_item)
        if parent.internalPointer() is None:
            return self.createIndex(row, col, self._root_item)
        else:
            parent_model_item = parent.internalPointer()
            model_item = parent_model_item.children()[row]
            return self.createIndex(row, 0, model_item)

    def columnCount(self, parent=None, *args, **kwargs):
        return 1

    def rowCount(self, parent=None, *args, **kwargs):
        if parent is None:
            return 1
        if parent.internalPointer() is None:
            return 1
        else:
            return len(parent.internalPointer().children())

    def data(self, index: QModelIndex, role=None):
        col = index.column()
        row = index.row()
        data = None
        model_item = index.internalPointer()
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return model_item.name
        elif role == Qt.DecorationRole:
            if type(model_item.data) is Parameters:
                return get_icon("params")
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


class DocumentModelItem(QObject):
    def __init__(self, data, model, parent=None, name="No name"):
        QObject.__init__(self, parent)
        self._data = data
        self._name = name
        self._model = model
        if data is not None:
            data.add_change_handler(self.data_changed)

    def __del__(self):
        # print("modelitem deleted")
        try:
            if self._data is not None:
                self._data.remove_change_handler(self.data_changed)
        except Exception as e:
            print(str(e))

    @property
    def name(self):
        if self._data is not None:
            if hasattr(self._data, "name"):
                return self._data.name
        return self._name

    @property
    def data(self):
        return self._data

    def data_changed(self, event):
        pass