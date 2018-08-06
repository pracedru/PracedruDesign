from PyQt5.QtCore import *
from Business import *
from Data.Materials import Material
from Data.Parameters import *

__author__ = 'mamj'

col_header = ["Materials"]


class MaterialsModel(QAbstractTableModel):
	def __init__(self, doc):
		QAbstractItemModel.__init__(self)
		self._materials = doc.get_materials()
		self._doc = doc
		self._rows = []
		for material_tuple in self._materials.get_materials():
			self._rows.append(material_tuple[1].uid)
		self._materials.add_change_handler(self.on_materials_changed)
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
			material_item = self._materials.get_material(self._rows[row])
			if col == 0:
				data = material_item.name
		elif int_role == Qt.EditRole:
			material_item = self._materials.get_material(self._rows[row])
			if col == 0:
				data = material_item.name
		return data

	def setData(self, model_index: QModelIndex, value: QVariant, int_role=None):
		col = model_index.column()
		row = model_index.row()
		material_item = self._materials.get_material(self._rows[row])
		if col == 0:
			material_item.set_name(value)
			return True

		return False

	def removeRow(self, row, QModelIndex_parent=None, *args, **kwargs):
		material = self._materials.get_material(self._rows[row])
		remove_materials(self._doc, [material])

	#  self._edges.remove_edge(edge)

	def remove_rows(self, rows):
		materials = []
		for row in rows:
			materials.append(self._materials.get_material(self._rows[row]))
		remove_materials(self._doc, materials)

	def on_materials_changed(self, event: ChangeEvent):
		if type(event.object) is Material:
			if event.type == event.BeforeObjectAdded:
				self.beginInsertRows(QModelIndex(), len(self._rows), len(self._rows))
			if event.type == event.ObjectAdded:
				self._rows.append(event.object.uid)
				self.endInsertRows()
			if event.type == event.BeforeObjectRemoved:
				if event.object.uid in self._rows:
					row = self._rows.index(event.object.uid)
					self.beginRemoveRows(QModelIndex(), row, row)
			if event.type == event.ObjectRemoved:
				if event.object.uid in self._rows:
					self._rows.remove(event.object.uid)
					self.endRemoveRows()
			if event.type == event.ValueChanged:
				mat = event.sender
				if type(mat) is Material:
					row = self._rows.index(mat.uid)
					left = self.createIndex(row, 0)
					right = self.createIndex(row, 3)
					self.dataChanged.emit(left, right)

		if event.type == event.Cleared:
			self.beginRemoveRows(QModelIndex(), 0, len(self._rows) - 1)
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

	def get_materials_object(self):
		return self._materials

	def get_material(self, row):
		return self._materials.get_material(self._rows[row])

	def get_index_from_edge(self, material):
		row = self._rows.index(material.uid)
		return self.index(row, 0)
