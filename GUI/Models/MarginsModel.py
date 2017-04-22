from PyQt5.QtCore import *
from Business import *

__author__ = 'mamj'

col_header = ["Margin Name"]


class MarginsModel(QAbstractTableModel):
    def __init__(self, doc):
        QAbstractItemModel.__init__(self)
        self._margins = doc.get_margins()
        self._doc = doc
        self._margins.add_change_handler(self.on_margins_changed)

    def rowCount(self, model_index=None, *args, **kwargs):
        return len(self._margins.get_margins())

    def columnCount(self, model_index=None, *args, **kwargs):
        return len(col_header)

    def data(self, model_index: QModelIndex, int_role=None):
        col = model_index.column()
        row = model_index.row()
        data = None
        if int_role == Qt.DisplayRole:
            margin_item = self._margins.get_margins()[row]
            if col == 0:
                data = margin_item.name
        elif int_role == Qt.EditRole:
            margin_item = self._margins.get_margins()[row]
            if col == 0:
                data = margin_item.name
        return data

    def setData(self, model_index: QModelIndex, value: QVariant, int_role=None):
        col = model_index.column()
        row = model_index.row()
        margin_item = self._margins.get_margins()[row]
        if col == 0:
            margin_item.set_name(value)
            return True
        return False

    def remove_rows(self, rows):
        margins = set()
        for row in rows:
            margins.add(self._margins.get_margins()[row])
        remove_margins(self._doc, margins)

    def on_margins_changed(self, event: ChangeEvent):
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

    def get_margins_object(self):
        return self._margins

    def get_margin(self, row):
        return self._margins.get_margins()[row]

    def get_index_from_margin(self, component):
        row = self._margins.get_margins().index(component)
        return self.index(row, 0)
