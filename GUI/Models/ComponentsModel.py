from PyQt5.QtCore import *
from Business import *
from Data.Components import Components

__author__ = 'mamj'

col_header = ["Components", "Type"]
types = ['Lines', 'Areas']


class ComponentsModel(QAbstractTableModel):
    def __init__(self, doc):
        QAbstractItemModel.__init__(self)
        self._components = doc.get_components()
        self._doc = doc
        self._components.add_change_handler(self.on_components_changed)

    def rowCount(self, model_index=None, *args, **kwargs):
        return len(self._components.get_components())

    def columnCount(self, model_index=None, *args, **kwargs):
        return len(col_header)

    def data(self, model_index: QModelIndex, int_role=None):
        col = model_index.column()
        row = model_index.row()
        data = None
        if int_role == Qt.DisplayRole:
            component_item = self._components.get_components()[row]
            if col == 0:
                data = component_item.name
            if col == 1:
                data = types[component_item.type-1]
        elif int_role == Qt.EditRole:
            component_item = self._components.get_components()[row]
            if col == 0:
                data = component_item.name
            elif col == 1:
                return types
        return data

    def setData(self, model_index: QModelIndex, value: QVariant, int_role=None):
        col = model_index.column()
        row = model_index.row()
        component_item = self._components.get_components()[row]
        if col == 0:
            component_item.name = value
            return True
        elif col == 1:
            component_item.type = value+1
        return False

    def removeRow(self, row, QModelIndex_parent=None, *args, **kwargs):
        component = self._components.get_components()[row]
        remove_components(self._doc, [component])

    def remove_rows(self, rows):
        components = set()
        for row in rows:
            components.add(self._components.get_components()[row])
        remove_components(self._doc, components)

    def on_components_changed(self, event: ChangeEvent):
        if type(event.sender) is Components:
            if event.type == event.BeforeObjectAdded:
                lenght = len(self._components.get_components())
                self.beginInsertRows(QModelIndex(), lenght, lenght)
            if event.type == event.ObjectAdded:
                self.endInsertRows()
            if event.type == event.BeforeObjectRemoved:
                if event.object in self._components.get_components():
                    row = self._components.get_components().index(event.object)
                    self.beginRemoveRows(QModelIndex(), row, row)
            if event.type == event.ObjectRemoved:
                if event.object in self._components.get_components():
                    self.endRemoveRows()
        if type(event.object) is Component:
            if event.type == event.ValueChanged:
                comp = event.sender
                row = self._components.get_components.index(comp)
                left = self.createIndex(row, 0)
                right = self.createIndex(row, 3)
                self.dataChanged.emit(left, right)

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

    def get_components_object(self):
        return self._components

    def get_component(self, row):
        return self._components.get_components()[row]

    def get_index_from_edge(self, component):
        row = self._components.get_components().index(component)
        return self.index(row, 0)

    def get_options(self, index):
        return types