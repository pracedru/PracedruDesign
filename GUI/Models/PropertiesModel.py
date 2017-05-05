import numpy
from PyQt5.QtCore import QAbstractTableModel
from PyQt5.QtCore import QLocale
from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import Qt
#from scipy.linalg._solve_toeplitz import float64

from Data.Drawings import Drawing
from Data.Point3d import KeyPoint
from Data.Sketch import Edge, Text, Sketch
from Data.Style import EdgeStyle

col_header = ["Value"]

rows_by_type = {
    "None": [],
    "Edge": [
        ['Name', 'name'],
        ['Style', 'style_name']],
    "Area": [
        ['Name', 'name'],
        ['Hatch', 'hatch']],
    "Attribute": [
        ['Attribute Name', 'name'],
        ['Default Value', 'value'],
        ['Height', 'height'],
        ['Angle', 'angle'],
        ['Horizontal Alignment', 'horizontal_alignment'],
        ['Vertical Alignment', 'vertical_alignment']],
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
        ['Orientation', 'orientation', {'choices': ['Landscape', 'Portrait']}],
        ['Header', 'header'],
        ['Margins', 'margins']],
    "EdgeStyle": [
        ['Name', 'name'],
        ['Thickness', 'thickness'],
        ['Color', 'color'],
        ['Line type', 'line_type']],
    "Feature": [
        ['Name', 'name'],
        ['Type', 'feature_type', {'choices': ['Extrude', 'Revolve', 'Fillet', 'Plane', 'Sketch']}],
        ['Length', 'distance', {'condition': ['feature_type', 0]}],
        ['Angles', 'distance', {'condition': ['feature_type', 1]}],
        ['Plane', 'plane', {'condition': ['feature_type', 4]}]],
    "Part": [
        ['Name', 'name']],
    "Field": [
        ['Name', 'name'],
        ['Value', 'value']],
    "SketchView": [
        ['Name', 'name'],
        ['Scale', 'scale'],
        ['Position', 'offset_values']
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
        type_name = type(item).__name__
        if type_name in rows_by_type:
            self._rows = list(rows_by_type[type_name])
            rows_to_remove = []
            for row in self._rows:
                if len(row) > 2:
                    row_spec = row[2]
                    if 'condition' in row_spec:
                        cond = row_spec['condition']
                        name = cond[0]
                        value = cond[1]
                        if getattr(self._item, name) != value:
                            rows_to_remove.append(row)
            for row in rows_to_remove:
                self._rows.remove(row)

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
            if type(data) is numpy.float64:
                data = float(data)
            if type(data) is float:
                data = QLocale().toString(data)
            if type(data) is int:
                if len(self._rows[row]) > 2:
                    row_spec = self._rows[row][2]
                    if 'choices' in row_spec:
                        return row_spec['choices'][data]
                else:
                    return data
            data = str(data)
        elif int_role == Qt.EditRole:
            data = getattr(self._item, self._rows[row][1])
            if type(data) is numpy.float64:
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
                if origin_type is numpy.float64:
                    value = numpy.float64(QLocale().toFloat(value)[0])
                if origin_type is int:
                    value = QLocale().toInt(value)[0]
                    if len(self._rows[row]) > 2:
                        row_spec = self._rows[row][2]
                        if 'choices' in row_spec:
                            if len(row_spec['choices']) <= value:
                                return False
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
        default_flags = Qt.ItemIsSelectable
        if self._item is not None:
            row = model_index.row()
            if row < len(self._rows):
                class_attribute = getattr(type(self._item), self._rows[row][1], None)
                if isinstance(class_attribute, property):
                    if class_attribute.fset is not None:
                        default_flags = default_flags | Qt.ItemIsEditable | Qt.ItemIsEnabled
        return default_flags
