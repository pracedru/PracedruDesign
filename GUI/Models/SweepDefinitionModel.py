from PyQt5.QtCore import *
from Business import *

__author__ = 'mamj'

col_header = ["Geometries", 'Divisions', 'offset', 'offset']


class SweepDefinitionModel(QAbstractTableModel):
	def __init__(self, doc):
		QAbstractItemModel.__init__(self)
		self._doc = doc
		self._sweep_definition = None

	def rowCount(self, model_index=None, *args, **kwargs):
		if self._sweep_definition is not None:
			return self._sweep_definition.length
		return 0

	def columnCount(self, model_index=None, *args, **kwargs):
		return len(col_header)

	def data(self, model_index: QModelIndex, int_role=None):
		col = model_index.column()
		row = model_index.row()
		data = None
		if int_role == Qt.DisplayRole:
			element = self._sweep_definition.get_elements()[row]
			if col == 0:
				data = element.name
			if col == 1:
				data = self._sweep_definition.get_divisions_of_element(element)
			if col == 2:
				data = self._sweep_definition.get_offset1_of_element(element)
			if col == 3:
				data = self._sweep_definition.get_offset2_of_element(element)
		elif int_role == Qt.EditRole:
			element = self._sweep_definition.get_elements()[row]
			if col == 0:
				data = element.name
			if col == 1:
				data = self._sweep_definition.get_divisions_of_element(element)
			if col == 2:
				data = QLocale().toString(self._sweep_definition.get_offset1_of_element(element))
			if col == 3:
				data = QLocale().toString(self._sweep_definition.get_offset2_of_element(element))
		return data

	def setData(self, model_index: QModelIndex, value: QVariant, int_role=None):
		col = model_index.column()
		row = model_index.row()
		element = self._sweep_definition.get_elements()[row]
		if col == 0:
			element.set_name(value)
			return True
		elif col == 1:
			self._sweep_definition.set_divisions_of_element(element, value)
			return True
		elif col == 2:
			parsed = QLocale().toDouble(value)
			if parsed[1]:
				self._sweep_definition.set_offset1_of_element(element, parsed[0])
				return True
		elif col == 3:
			parsed = QLocale().toDouble(value)
			if parsed[1]:
				self._sweep_definition.set_offset2_of_element(element, parsed[0])
				return True
		return False

	def removeRow(self, row, QModelIndex_parent=None, *args, **kwargs):
		element = self._sweep_definition.get_elements()[row]
		remove_sweep_elements(self._doc, self._sweep_definition, [element])

	def remove_rows(self, rows):
		elements = []
		for row in rows:
			elements.append(self._sweep_definition.get_elements()[row])
		remove_sweep_elements(self._doc, self._sweep_definition, elements)

	def on_sweep_def_changed(self, event: ChangeEvent):
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

	def set_sweep_definition(self, sweep_definition):
		if self._sweep_definition is not None:
			self._sweep_definition.remove_change_handler(self.on_sweep_def_changed)
		self._sweep_definition = sweep_definition
		if sweep_definition is not None:
			sweep_definition.add_change_handler(self.on_sweep_def_changed)
		self.layoutChanged.emit()

	def get_sweep_definition(self):
		return self._sweep_definition

	def get_element(self, row):
		return self._sweep_definition.get_elements()[row]

	def get_index_from_element(self, element):
		row = self._components.get_elements().index(element)
		return self.index(row, 0)
