from enum import EnumMeta

import numpy
from PyQt5.QtCore import QAbstractTableModel, QSize
from PyQt5.QtCore import QLocale
from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import Qt

from Business.Undo import change_property
from Data.Feature import FeatureType
from Data.Sketch import *
from GUI.init import gui_scale

col_header = ["Value"]

rows_by_type = {
	"None": [],
	"Edge": [
		['Name', 'name'],
		['Style', 'style_name'],
		['Type', 'type_name'],
		['Radius', {'name': 'get_meta_data', 'args': ['r', None], 'setName': 'set_meta_data'}, {'condition': ['type', EdgeType.CircleEdge]}],
		['Radius', {'name': 'get_meta_data', 'args': ['r', None], 'setName': 'set_meta_data'}, {'condition': ['type', EdgeType.ArcEdge]}],
		['Start angle', {'name': 'get_meta_data', 'args': ['sa', None], 'setName': 'set_meta_data'}, {'condition': ['type', EdgeType.ArcEdge]}],
		['End angle', {'name': 'get_meta_data', 'args': ['ea', None], 'setName': 'set_meta_data'}, {'condition': ['type', EdgeType.ArcEdge]}]],
	"SketchInstance": [
		['Name', 'name'],
		['Scale', 'scale'],
		['Rotation', 'rotation']],
	"EdgeLoopArea": [
		['Name', 'name'],
		['Brush', 'brush_name'],
		['Brush angle', 'brush_rotation']],
	"CompositeArea": [
		['Name', 'name'],
		['Brush', 'brush_name'],
		['Brush angle', 'brush_rotation']],
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
	"Brush": [
		['Name', 'name'],
		['Type', 'type']],
	"HatchStyle": [
		['Name', 'name']],
	"Feature": [
		['Name', 'name'],
		['Type', 'feature_type', {'choices': ['Extrude', 'Revolve', 'Fillet', 'Plane', 'Sketch', 'Nurbs Surface']}],
		['Length', 'distance', {'condition': ['feature_type', FeatureType.ExtrudeFeature]}],
		['Angles', 'distance', {'condition': ['feature_type', FeatureType.RevolveFeature]}],
		['Plane', 'plane', {'condition': ['feature_type', FeatureType.SketchFeature]}]],
	"Part": [
		['Name', 'name'],
		['Color', 'color'],
		['Hardness', 'specular']],
	"Field": [
		['Name', 'name'],
		['Value', 'value']],
	"SketchView": [
		['Name', 'name'],
		['Scale', 'scale_name'],
		['Position', 'offset_values']],
	"PartView": [
		['Name', 'name'],
		['Scale', 'scale'],
		['Position', 'offset_values']],
	"Parameter": [
		['Name', 'name'],
		['Value', 'value_view'],
		['Formula', 'formula'],
		['Base unit', 'base_unit'],
		['Hidden', 'hidden'],
		['Locked', 'locked']
	]
}


class PropertiesModel(QAbstractTableModel):
	ComboBoxRole = 9878

	def __init__(self, document):
		QAbstractTableModel.__init__(self)
		self._document = document
		self._item = None
		self._rows = []
		self._gui_scale = gui_scale()

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
		if type(self._rows[row][1]) == str:
			data = getattr(self._item, self._rows[row][1])
		else:
			func_name = self._rows[row][1]['name']
			args = self._rows[row][1]['args']
			data = getattr(self._item, func_name)(*args)
		if int_role == Qt.DisplayRole:
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
			if isinstance(data, Enum):
				if len(self._rows[row]) == 3:
					row_spec = self._rows[row][2]
					if 'choices' in row_spec:
						if data.value in row_spec['choices']:
							data = row_spec['choices'][data.value]
						else:
							data = data.name
					else:
						data = data.name
				else:
					data = data.name
			data = str(data)
		elif int_role == Qt.EditRole:
			# data = getattr(self._item, self._rows[row][1])
			if type(data) is numpy.float64:
				data = float(data)
			if type(data) is float:
				data = QLocale().toString(data)
			if isinstance(data, Enum):
				enumData = data
				data = []
				for item in type(enumData):
					data.append(item.name)
				return data
			data = str(data)
		else:
			data = None
		return data

	def setData(self, model_index: QModelIndex, value, role=None):
		success = False
		col = model_index.column()
		row = model_index.row()
		if type(self._rows[row][1]) is str:
			attr_name = self._rows[row][1]
			origin_type = type(getattr(self._item, attr_name))
		else:  # This is a meta data object
			func_name = self._rows[row][1]['name']
			args = self._rows[row][1]['args']
			data = getattr(self._item, func_name)(*args)
			origin_type = type(data)
			attr_name = self._rows[row][1]['setName']

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
				if callable(getattr(self._item, attr_name)):
					args = self._rows[row][1]['args'].copy()
					args.append(value)
					getattr(self._item, attr_name)(*args)
				else:
					change_property(self._document, self._item, self._rows[row][1], value)
				# setattr(self._item, self._rows[row][1], value)
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
		elif int_role == Qt.SizeHintRole:
			if orientation == Qt.Horizontal:
				return QSize(220 * self._gui_scale, 22 * self._gui_scale)
		else:
			return None

	def flags(self, model_index: QModelIndex):
		default_flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
		if self._item is not None:
			row = model_index.row()
			if row < len(self._rows):
				if type(self._rows[row][1]) == str:
					attr_name = self._rows[row][1]
					class_attribute = getattr(type(self._item), attr_name, None)
					if isinstance(class_attribute, property):
						if class_attribute.fset is not None:
							default_flags = default_flags | Qt.ItemIsEditable
				else:
					if 'setName' in self._rows[row][1]:
						default_flags = default_flags | Qt.ItemIsEditable
		return default_flags
