from PyQt5.QtCore import *
from Business import *

__author__ = 'mamj'

col_header = ["Mesh definitions", "Type", "Size"]
types = ['Edge Division', 'Edge Element Size', 'Area Element Size', 'Global Element Size']


class MeshModel(QAbstractTableModel):
    def __init__(self, doc):
        QAbstractItemModel.__init__(self)
        self._mesh = doc.get_mesh()
        self._doc = doc
        self._mesh.add_change_handler(self.on_mesh_definition_changed)

    def rowCount(self, model_index=None, *args, **kwargs):
        return len(self._mesh.get_mesh_definitions())

    def columnCount(self, model_index=None, *args, **kwargs):
        return len(col_header)

    def data(self, model_index: QModelIndex, int_role=None):
        col = model_index.column()
        row = model_index.row()
        data = None
        if int_role == Qt.DisplayRole:
            mesh_def_item = self._mesh.get_mesh_definitions()[row]
            if col == 0:
                data = mesh_def_item.name
            if col == 1:
                data = types[mesh_def_item.type - 1]
            elif col == 2:
                data = mesh_def_item.size
        elif int_role == Qt.EditRole:
            mesh_def_item = self._mesh.get_mesh_definitions()[row]
            if col == 0:
                data = mesh_def_item.name
            elif col == 1:
                return types
            elif col == 2:
                return QLocale().toString(mesh_def_item.size)
        return data

    def setData(self, model_index: QModelIndex, value: QVariant, int_role=None):
        col = model_index.column()
        row = model_index.row()
        mesh_def_item = self._mesh.get_mesh_definitions()[row]
        if col == 0:
            mesh_def_item.name = value
            return True
        elif col == 1:
            mesh_def_item.type = value + 1
            return True
        elif col == 2:
            parsed = QLocale().toDouble(value)
            if parsed[1]:
                mesh_def_item.size = parsed[0]
                return True
            else:
                return False
        return False

    def removeRow(self, row, QModelIndex_parent=None, *args, **kwargs):
        mesh_def_item = self._mesh.get_mesh_definitions()[row]
        remove_mesh_definitions(self._doc, [mesh_def_item])

    def remove_rows(self, rows):
        mesh_def_items = set()
        for row in rows:
            mesh_def_items.add(self._mesh.get_mesh_definitions()[row])
        remove_mesh_definitions(self._doc, mesh_def_items)

    def on_mesh_definition_changed(self, event: ChangeEvent):
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

    def get_mesh_object(self):
        return self._mesh

    def get_mesh_definition(self, row):
        return self._mesh.get_mesh_definitions()[row]

    def get_index_from_mesh_definition(self, mesh_definition):
        row = self._mesh.get_mesh_definitions().index(mesh_definition)
        return self.index(row, 0)

    def get_options(self, index):
        return types
