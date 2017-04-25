from PyQt5.QtCore import QAbstractTableModel
from PyQt5.QtCore import QLocale
from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import Qt
from scipy.linalg._solve_toeplitz import float64

from Data.Drawings import Drawing
from Data.Point3d import KeyPoint
from Data.Sketch import Edge, Text, Sketch

col_header = ["Value"]

rows_by_type = {
    "Edge": [
        ['Name', 'name']],
    "Text": [
        ['Name', 'name'],
        ['Value', 'value'],
        ['Height', 'height'],
        ['Angle', 'angle'],
        ['Horizontal Alignment', 'horizontal_alignment'],
        ['Vertical Alignment', 'vertical_alignment']],
    "KeyPoint": [
        ['X Coordinate', 'x'],
        ['Y Coordinate', 'y'],
        ['Z Coordinate', 'z']],
    "Sketch": [
        ['Name', 'name'],
        ['KeyPoints', 'key_point_count'],
        ['Edges', 'edges_count']],
    "Drawing": [
        ['Name', 'name'],
        ['Size', 'size'],
        ['Orientation', 'orientation'],
        ['Header', 'header'],
        ['Margins', 'margins']
    ]
}


class PropertiesModel(QAbstractTableModel):
    def __init__(self, document):
        QAbstractTableModel.__init__(self)
        self._document = document
        self._item = None
        self._rows = []

    def set_item(self, item):
        if item is None:
            return
        self.layoutAboutToBeChanged.emit()
        if self._item is not None:
            self._item.remove_change_handler(self.on_item_changed)
        self._item = item
        if type(item) is Edge:
            self._rows = rows_by_type['Edge']
        elif type(item) is Text:
            self._rows = rows_by_type['Text']
        elif type(item) is KeyPoint:
            self._rows = rows_by_type['KeyPoint']
        elif type(item) is Sketch:
            self._rows = rows_by_type['Sketch']
        elif type(item) is Drawing:
            self._rows = rows_by_type['Drawing']
        else:
            self._rows = []
        self.layoutChanged.emit()
        item.add_change_handler(self.on_item_changed)

    def on_item_changed(self, event):
        self.layoutAboutToBeChanged.emit()
        self.layoutChanged.emit()

    def rowCount(self, model_index=None, *args, **kwargs):
        return len(self._rows)

    def columnCount(self, model_index=None, *args, **kwargs):
        return len(col_header)

    def data(self, model_index: QModelIndex, int_role=None):
        col = model_index.column()
        row = model_index.row()
        if self._item is None:
            return None
        data = None
        if int_role == Qt.DisplayRole:
            data = getattr(self._item, self._rows[row][1])
            if type(data) is float64:
                data = float(data)
            if type(data) is float:
                data = QLocale().toString(data)
            data = str(data)
        elif int_role == Qt.EditRole:
            data = getattr(self._item, self._rows[row][1])
            if type(data) is float64:
                data = float(data)
            if type(data) is float:
                data = QLocale().toString(data)
            data = str(data)
        return data

    def setData(self, model_index: QModelIndex, value, role=None):
        col = model_index.column()
        row = model_index.row()
        origin_type = type(getattr(self._item, self._rows[row][1]))
        if role == Qt.EditRole:
            try:
                if origin_type is float:
                    value = QLocale().toFloat(value)[0]
                if origin_type is float64:
                    value = float64(QLocale().toFloat(value)[0])
                if origin_type is int:
                    value = QLocale().toInt(value)[0]
                if origin_type is list:
                    value = eval(value)
                setattr(self._item, self._rows[row][1], value)
                success = True
            except Exception as e:
                success = False
        return success

    def headerData(self, p_int, orientation, int_role=None):
        if int_role == Qt.DisplayRole:
            if orientation == Qt.Vertical:
                return self._rows[p_int][0]
            else:
                return col_header[p_int]

        else:
            return

    def flags(self, model_index: QModelIndex):
        default_flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
        return default_flags