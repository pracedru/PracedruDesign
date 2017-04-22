from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMessageBox

from Business import remove_areas
from Data import Areas
from Data.Parameters import *

__author__ = 'mamj'

col_header = ["Areas"]


class AreasModel(QAbstractTableModel):
    def __init__(self, doc):
        QAbstractItemModel.__init__(self)
        self._areas = doc.get_areas()
        self._rows = []
        self._doc = doc
        for area_tuple in self._areas.get_areas():
            self._rows.append(area_tuple[1].uid)
        self._areas.add_change_handler(self.on_areas_changed)
        self.old_row_count = 0

    def rowCount(self, model_index=None, *args, **kwargs):
        return len(self._rows)

    def columnCount(self, model_index=None, *args, **kwargs):
        return len(col_header)

    def data(self, model_index: QModelIndex, int_role=None):
        col = model_index.column()
        row = model_index.row()
        data = None
        if int_role == Qt.DisplayRole:
            area_item = self._areas.get_area_item(self._rows[row])
            if col == 0:
                data = area_item.name
        elif int_role == Qt.EditRole:
            area_item = self._areas.get_area_item(self._rows[row])
            if col == 0:
                data = area_item.name
        return data

    def setData(self, model_index: QModelIndex, value: QVariant, int_role=None):
        col = model_index.column()
        row = model_index.row()
        area_item = self._areas.get_area_item(self._rows[row])
        if col == 0:
            area_item.set_name(value)
            return True

        return False

    def removeRow(self, row, QModelIndex_parent=None, *args, **kwargs):
        area = self._areas.get_area_item(self._rows[row])
        remove_areas(self._doc, [area])

    def remove_rows(self, rows):
        areas = []
        for row in rows:
            areas.append(self._areas.get_area_item(self._rows[row]))
        remove_areas(self._doc, areas)

    def on_areas_changed(self, event: ChangeEvent):
        if event.type == event.BeforeObjectAdded:
            self.beginInsertRows(QModelIndex(), len(self._rows), len(self._rows))
        if event.type == event.ObjectAdded:
            self._rows.append(event.object.uid)
            self.endInsertRows()
        if event.type == event.BeforeObjectRemoved:
            try:
                row = self._rows.index(event.object.uid)
                self.beginRemoveRows(QModelIndex(), row, row)
            except ValueError:
                pass
        if event.type == event.ObjectRemoved:
            try:
                self._rows.remove(event.object.uid)
                self.endRemoveRows()
            except ValueError:
                pass
        if event.type == event.Cleared:
            self.beginRemoveRows(QModelIndex(), 0, len(self._rows)-1)
            self._rows = []
            self.endRemoveRows()

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

    def get_areas_object(self):
        return self._areas

    def get_area(self, row):
        return self._areas.get_area_item(self._rows[row])

    def get_index_from_area(self, area):
        row = self._rows.index(area.uid)
        return self.index(row, 0)
