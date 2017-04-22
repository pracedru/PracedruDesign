from PyQt5.QtCore import *
from Business import *

__author__ = 'mamj'

col_header = ["Edge Name"]


class MarginModel(QAbstractTableModel):
    def __init__(self, doc):
        QAbstractItemModel.__init__(self)
        self._doc = doc
        self._margin = None

    def rowCount(self, model_index=None, *args, **kwargs):
        if self._margin is not None:
            return self._margin.length
        return 0

    def columnCount(self, model_index=None, *args, **kwargs):
        return len(col_header)

    def data(self, model_index: QModelIndex, int_role=None):
        col = model_index.column()
        row = model_index.row()
        data = None
        if int_role == Qt.DisplayRole:
            edge = self._margin.get_edges()[row]
            if col == 0:
                data = edge.name
        elif int_role == Qt.EditRole:
            edge = self._margin.get_edges()[row]
            if col == 0:
                data = edge.name
        return data

    def setData(self, model_index: QModelIndex, value: QVariant, int_role=None):
        col = model_index.column()
        row = model_index.row()
        edge = self._margin.get_edges()[row]
        if col == 0:
            edge.set_name(value)
            return True
        return False

    def removeRow(self, row, QModelIndex_parent=None, *args, **kwargs):
        edge = self._margin.get_edges()[row]
        remove_edges_from_margin(self._doc, self._margin, [edge])

    def remove_rows(self, rows):
        edges = []
        for row in rows:
            edges.append(self._margin.get_edges()[row])
        remove_edges_from_margin(self._doc, self._margin, edges)

    def on_margin_changed(self, event: ChangeEvent):
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

    def set_margin(self, margin):
        if self._margin is not None:
            self._margin.remove_change_handler(self.on_margin_changed)
        self._margin = margin
        if margin is not None:
            margin.add_change_handler(self.on_margin_changed)
        self.layoutChanged.emit()

    def get_margin(self):
        return self._margin

    def get_edge(self, row):
        return self._margin.get_edges()[row]

    def get_index_from_edge(self, edge):
        row = self._components.get_elements().index(edge)
        return self.index(row, 0)
