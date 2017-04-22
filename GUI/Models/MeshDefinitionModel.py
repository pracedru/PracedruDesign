from PyQt5.QtCore import *
from Business import *

__author__ = 'mamj'

col_header = ["Geometries"]


class MeshDefinitionModel(QAbstractTableModel):
    def __init__(self, doc):
        QAbstractItemModel.__init__(self)
        self._doc = doc
        self._mesh_definition = None

    def rowCount(self, model_index=None, *args, **kwargs):
        if self._mesh_definition is not None:
            return self._mesh_definition.length
        return 0

    def columnCount(self, model_index=None, *args, **kwargs):
        return len(col_header)

    def data(self, model_index: QModelIndex, int_role=None):
        col = model_index.column()
        row = model_index.row()
        data = None
        if int_role == Qt.DisplayRole:
            element = self._mesh_definition.get_elements()[row]
            if col == 0:
                data = element.name
        elif int_role == Qt.EditRole:
            element = self._mesh_definition.get_elements()[row]
            if col == 0:
                data = element.name
        return data

    def setData(self, model_index: QModelIndex, value: QVariant, int_role=None):
        col = model_index.column()
        row = model_index.row()
        element = self._mesh_definition.get_elements()[row]
        if col == 0:
            element.set_name(value)
            return True
        return False

    def removeRow(self, row, QModelIndex_parent=None, *args, **kwargs):
        element = self._mesh_definition.get_elements()[row]
        remove_mesh_elements(self._doc, self._mesh_definition, [element])

    def remove_rows(self, rows):
        elements = []
        for row in rows:
            elements.append(self._mesh_definition.get_elements()[row])
        remove_mesh_elements(self._doc, self._mesh_definition, elements)

    def on_mesh_def_changed(self, event: ChangeEvent):
        self.layoutChanged.emit()

    def flags(self, model_index: QModelIndex):
        default_flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
        return default_flags

    def headerData(self, p_int, orientation, int_role=None):
        if int_role == Qt.DisplayRole:
            if orientation == Qt.Vertical:
                return p_int
            else:
                return col_header[p_int]

        else:
            return

    def set_mesh_definition(self, mesh_definition):
        if self._mesh_definition is not None:
            self._mesh_definition.remove_change_handler(self.on_mesh_def_changed)
        self._mesh_definition = mesh_definition
        if mesh_definition is not None:
            mesh_definition.add_change_handler(self.on_mesh_def_changed)
        self.layoutChanged.emit()

    def get_mesh_definition(self):
        return self._mesh_definition

    def get_element(self, row):
        return self._mesh_definition.get_elements()[row]

    def get_index_from_element(self, element):
        row = self._components.get_elements().index(element)
        return self.index(row, 0)
