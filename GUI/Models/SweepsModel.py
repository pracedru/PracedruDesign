from PyQt5.QtCore import *
from Business import *

__author__ = 'mamj'

col_header = ["Sweep definitions", "Type"]
types = ['Area sweep', 'Line sweep']


class SweepsModel(QAbstractTableModel):
	def __init__(self, doc):
		QAbstractItemModel.__init__(self)
		self._sweeps = doc.get_sweeps()
		self._doc = doc
		self._sweeps.add_change_handler(self.on_sweep_definition_changed)

	def rowCount(self, model_index=None, *args, **kwargs):
		return len(self._sweeps.get_sweep_definitions())

	def columnCount(self, model_index=None, *args, **kwargs):
		return len(col_header)

	def data(self, model_index: QModelIndex, int_role=None):
		col = model_index.column()
		row = model_index.row()
		data = None
		if int_role == Qt.DisplayRole:
			sweep_def_item = self._sweeps.get_sweep_definitions()[row]
			if col == 0:
				data = sweep_def_item.name
			if col == 1:
				data = types[sweep_def_item.type - 1]
		elif int_role == Qt.EditRole:
			sweep_def_item = self._sweeps.get_sweep_definitions()[row]
			if col == 0:
				data = sweep_def_item.name
			elif col == 1:
				return types

		return data

	def setData(self, model_index: QModelIndex, value: QVariant, int_role=None):
		col = model_index.column()
		row = model_index.row()
		sweep_def_item = self._sweeps.get_sweep_definitions()[row]
		if col == 0:
			sweep_def_item.name = value
			return True
		elif col == 1:
			sweep_def_item.type = value + 1
		return False

	def removeRow(self, row, QModelIndex_parent=None, *args, **kwargs):
		sweep_def_item = self._sweeps.get_sweep_definitions()[row]
		remove_sweep_definitions(self._doc, [sweep_def_item])

	def remove_rows(self, rows):
		sweep_def_items = set()
		for row in rows:
			sweep_def_items.add(self._sweeps.get_sweep_definitions()[row])
		remove_sweep_definitions(self._doc, sweep_def_items)

	def on_sweep_definition_changed(self, event: ChangeEvent):
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

	def get_sweep_object(self):
		return self._sweeps

	def get_sweep_definition(self, row):
		return self._sweeps.get_sweep_definitions()[row]

	def get_index_from_sweep_definition(self, sweep_definition):
		row = self._sweeps.get_sweep_definitions().index(sweep_definition)
		return self.index(row, 0)

	def get_options(self, index):
		return types
