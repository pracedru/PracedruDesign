from PyQt5.QtCore import QAbstractItemModel
from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import QObject
from PyQt5.QtCore import Qt

from Data.Document import Document
from Data.Events import ChangeEvent
from Data.Geometry import Geometry
from Data.Parameters import Parameters, Parameter
from Data.Point3d import KeyPoint
from Data.Sketch import Sketch, Edge
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
        glocal_params_item = DocumentModelItem(self._doc.get_parameters(), self, self._root_item)
        for param_tuple in self._doc.get_parameters().get_all_parameters():
            param_item = DocumentModelItem(param_tuple[1], self, glocal_params_item)
        geoms_item = DocumentModelItem(self._doc.get_geometries(), self, self._root_item)
        for geom_tuple in self._doc.get_geometries().items():
            if type(geom_tuple[1]) is Sketch:
                self.populate_sketch(geom_tuple[1], geoms_item)


        DocumentModelItem(None, self, self._root_item, "Analyses")
        DocumentModelItem(None, self, self._root_item, "Drawings")
        DocumentModelItem(None, self, self._root_item, "Reports")

    def populate_sketch(self, sketch, geoms_item):
        geom_item = self.create_model_item(geoms_item, sketch)
        for param_tuple in sketch.get_all_local_parameters():
            param_item = DocumentModelItem(param_tuple[1], self, geom_item.children()[0])
        for kp_tuple in sketch.get_key_points():
            param_item = DocumentModelItem(kp_tuple[1], self, geom_item.children()[1], "Key point")
        for edge_tuple in sketch.get_edges():
            param_item = DocumentModelItem(edge_tuple[1], self, geom_item.children()[2])

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
            elif type(model_item.data) is Parameter:
                return get_icon("param")
            elif type(model_item.data) is Sketch:
                return get_icon("sketch")
            elif type(model_item.data) is KeyPoint:
                return get_icon("kp")
            elif type(model_item.data) is Edge:
                return get_icon("edge")
            return get_icon("default")
        return None

    def setData(self, index: QModelIndex, value, role=None):
        model_item = index.internalPointer()
        if role==Qt.EditRole:
            model_item.data.name = str(value)
            return True
        return False

    def headerData(self, p_int, qt_orientation, role=None):
        if role == Qt.DisplayRole:
            if qt_orientation == Qt.Vertical:
                return p_int
            else:
                return "Name"

    def flags(self, index: QModelIndex):
        col = index.column()
        row = index.row()
        model_item = index.internalPointer()
        default_flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if isinstance(model_item.data, Geometry):
            default_flags = default_flags | Qt.ItemIsEditable
        if isinstance(model_item.data, Parameter):
            default_flags = default_flags | Qt.ItemIsEditable
        return default_flags

    def on_document_changed(self, event):
        self.layoutChanged.emit()

    def on_before_object_added(self, parent_item, object):
        self.layoutAboutToBeChanged.emit()

    def on_object_added(self, parent_item, object):
        self.create_model_item(parent_item, object)

    def create_model_item(self, parent_item, object):
        if type(parent_item.data) is Sketch:
            if type(object) is Parameter:
                parameters_item = parent_item.children()[0]
                new_item = DocumentModelItem(object, self, parameters_item)
            elif type(object) is KeyPoint:
                kps_item = parent_item.children()[1]
                new_item = DocumentModelItem(object, self, kps_item, "Key point")
            elif type(object) is Edge:
                edges_item = parent_item.children()[2]
                new_item = DocumentModelItem(object, self, edges_item)
        else:
            new_item = DocumentModelItem(object, self, parent_item)
            if type(object) is Sketch:
                DocumentModelItem(None, self, new_item, "Parameters")
                DocumentModelItem(None, self, new_item, "Key Points")
                DocumentModelItem(None, self, new_item, "Edges")
            self.layoutChanged.emit()
        return new_item

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

    def data_changed(self, event: ChangeEvent):
        if event.type == ChangeEvent.BeforeObjectAdded:
            self._model.on_before_object_added(self, event.object)
        if event.type == ChangeEvent.ObjectAdded:
            self._model.on_object_added(self, event.object)
