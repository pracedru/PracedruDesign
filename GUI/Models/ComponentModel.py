from PyQt5.QtCore import *
from Business import *

__author__ = 'mamj'

col_header = ["Geometries"]


class ComponentModel(QAbstractTableModel):
	def __init__(self, doc):
		QAbstractItemModel.__init__(self)
		self._doc = doc
		self._component = None

	def rowCount(self, model_index=None, *args, **kwargs):
		if self._component is not None:
			return self._component.length
		return 0

	def columnCount(self, model_index=None, *args, **kwargs):
		return len(col_header)

	def data(self, model_index: QModelIndex, int_role=None):
		col = model_index.column()
		row = model_index.row()
		data = None
		if int_role == Qt.DisplayRole:
			element = self._component.get_elements()[row]
			if col == 0:
				data = element.name
		elif int_role == Qt.EditRole:
			element = self._component.get_elements()[row]
			if col == 0:
				data = element.name
		return data

	def setData(self, model_index: QModelIndex, value: QVariant, int_role=None):
		col = model_index.column()
		row = model_index.row()
		element = self._component.get_elements()[row]
		if col == 0:
			element.set_name(value)
			return True
		return False

	def removeRow(self, row, QModelIndex_parent=None, *args, **kwargs):
		element = self._component.get_elements()[row]
		remove_component_elements(self._doc, [element])

	def remove_rows(self, rows):
		elements = []
		for row in rows:
			elements.append(self._component.get_elements()[row])
		remove_component_elements(self._component, elements)

	def on_component_changed(self, event: ChangeEvent):
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

	def set_component(self, component):
		if self._component is not None:
			self._component.remove_change_handler(self.on_component_changed)
		self._component = component
		if component is not None:
			component.add_change_handler(self.on_component_changed)
		self.layoutChanged.emit()

	def get_component(self):
		return self._component

	def get_element(self, row):
		return self._component.get_elements()[row]

	def get_index_from_edge(self, element):
		row = self._components.get_elements().index(element)
		return self.index(row, 0)
