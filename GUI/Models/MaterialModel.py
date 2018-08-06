from PyQt5.QtCore import QAbstractItemModel, QModelIndex, QVariant, Qt
from PyQt5.QtCore import QLocale
from PyQt5.QtGui import QIcon

from Data.Events import ChangeEvent
from GUI.Icons import get_icon

__author__ = 'mamj'

col_header = ["Name", "Value"]
rows = ['Name', 'Number', "Allowable stress", "Young's modulus", "Poisson's ratio", 'Alpha', "K", "Areas"]
rows_t = ['n', 'nu', 'sa', 'y', 'p', 'a', 'k', 'ar']


class MaterialModel(QAbstractItemModel):
	def __init__(self, doc):
		QAbstractItemModel.__init__(self)
		self._material = None

	def rowCount(self, model_index: QModelIndex = None, *args, **kwargs):
		if model_index.parent() is None:
			return len(self._rows)
		if model_index is None:
			return len(self._rows)
		else:
			pntr = model_index.internalPointer()
			if self._material is not None:
				if pntr == rows[2]:
					return len(self._material.get_allow_stresses()) + 1
				if pntr == rows[3]:
					return len(self._material.get_youngs_moduli()) + 1
				if pntr == rows[4]:
					return len(self._material.get_poissons_ratios()) + 1
				if pntr == rows[5]:
					return len(self._material.get_alphas()) + 1
				if pntr == rows[6]:
					return len(self._material.get_ks()) + 1
				if pntr == rows[7]:
					return len(self._material.get_areas())
			if pntr is None:
				return len(rows)
		return 0

	def columnCount(self, model_index=None, *args, **kwargs):
		return len(col_header)

	def data(self, model_index: QModelIndex, int_role=None):
		col = model_index.column()
		row = model_index.row()
		data = None
		pntr = model_index.internalPointer()

		if int_role == Qt.DisplayRole or int_role == Qt.EditRole:
			if pntr in rows:
				if col == 0:
					data = pntr
				elif row == 0:
					if self._material is not None:
						data = self._material.name
				elif row == 1:
					if self._material is not None:
						data = self._material.number
				elif row == 2:
					data = "MPa"
				elif row == 3:
					data = "GPa"
				elif row == 4:
					data = ""
				elif row == 5:
					data = "10^-6/K"
				elif row == 6:
					data = "W/K"
			else:
				if self._material is not None:
					if pntr in rows_t:
						if row == self.rowCount(model_index.parent()) - 1 and model_index.parent().row() < 7:
							return "New"
						if rows_t.index(pntr) == 2:
							if col == 0:
								data = self._material.get_allow_stresses()[row][col] - 273.15
							else:
								data = self._material.get_allow_stresses()[row][col] / 1e6
						if rows_t.index(pntr) == 3:
							if col == 0:
								data = self._material.get_youngs_moduli()[row][col] - 273.15
							else:
								data = self._material.get_youngs_moduli()[row][col] / 1e9
						elif rows_t.index(pntr) == 4:
							if col == 0:
								data = self._material.get_poissons_ratios()[row][col] - 273.15
							else:
								data = self._material.get_poissons_ratios()[row][col]
						elif rows_t.index(pntr) == 5:
							if col == 0:
								data = self._material.get_alphas()[row][col] - 273.15
							else:
								data = self._material.get_alphas()[row][col] * 1e6
						elif rows_t.index(pntr) == 6:
							if col == 0:
								data = self._material.get_ks()[row][col] - 273.15
							else:
								data = self._material.get_ks()[row][col]
						elif rows_t.index(pntr) == 7:
							if col == 0:
								data = self._material.get_areas()[row].name

		elif int_role == Qt.EditRole:
			if self._material is not None:
				material_item = self._materials.get_material(self._rows[row])
		elif int_role == Qt.DecorationRole:
			if pntr in rows_t:
				if row == self.rowCount(model_index.parent()) - 1 and model_index.parent().row() < 7:
					return get_icon("add")

		return data

	def setData(self, model_index: QModelIndex, value: QVariant, int_role=None):
		col = model_index.column()
		row = model_index.row()
		pntr = model_index.internalPointer()
		if int_role == Qt.EditRole:
			if pntr in rows:
				if row == 0:
					if self._material is not None:
						self._material.set_name(value)
						return True
				if row == 1:
					if self._material is not None:
						self._material.number = value
						return True
			if pntr in rows_t:
				data = (value, 1)
				if data[1] == 0:
					return False
				if rows_t.index(pntr) == 2:
					if row == self.rowCount(model_index.parent()) - 1:
						data = QLocale().toDouble(value)
						temp = None
						val = None
						if col == 0:
							temp = data[0] + 273.15
						else:
							val = data[0] * 1e6
						self._material.add_allowable_stress(temp, val)
						return True
					if col == 0:
						self._material.get_allow_stresses()[row][col] = data[0] + 273.15
					else:
						self._material.get_allow_stresses()[row][col] = data[0] * 1e6
				if rows_t.index(pntr) == 3:
					if row == self.rowCount(model_index.parent()) - 1:
						data = QLocale().toDouble(value)
						temp = None
						val = None
						if col == 0:
							temp = data[0] + 273.15
						else:
							val = data[0] * 1e9
						self._material.add_youngs_modulus(temp, val)
						return True
					if col == 0:
						self._material.get_youngs_moduli()[row][col] = data[0] + 273.15
					else:
						self._material.get_youngs_moduli()[row][col] = data[0] * 1e9
				elif rows_t.index(pntr) == 4:
					if row == self.rowCount(model_index.parent()) - 1:
						data = QLocale().toDouble(value)
						temp = None
						val = None
						if col == 0:
							temp = data[0] + 273.15
						else:
							val = data[0]
						self._material.add_poissons_ratio(temp, val)
						return True
					if col == 0:
						self._material.get_poissons_ratios()[row][col] = data[0] + 273.15
					else:
						self._material.get_poissons_ratios()[row][col] = data[0]
				elif rows_t.index(pntr) == 5:
					if row == self.rowCount(model_index.parent()) - 1:
						data = QLocale().toDouble(value)
						temp = None
						val = None
						if col == 0:
							temp = data[0] + 273.15
						else:
							val = data[0] / 1e6
						self._material.add_alpha(temp, val)
						return True
					if col == 0:
						self._material.get_alphas()[row][col] = data[0] + 273.15
					else:
						self._material.get_alphas()[row][col] = data[0] / 1e6
				elif rows_t.index(pntr) == 6:
					if row == self.rowCount(model_index.parent()) - 1:
						data = QLocale().toDouble(value)
						temp = None
						val = None
						if col == 0:
							temp = data[0] + 273.15
						else:
							val = data[0]
						self._material.add_k(temp, val)
						return True
					if col == 0:
						self._material.get_ks()[row][col] = data[0] + 273.15
					else:
						self._material.get_ks()[row][col] = data[0]
				elif rows_t.index(pntr) == 7:
					return False
				self._material.changed(ChangeEvent(self._material, ChangeEvent.ValueChanged, self._material))
				return True

		return False

	def parent(self, index: QModelIndex = None):
		if not index.isValid():
			return QModelIndex()
		pntr = index.internalPointer()
		parent_row = 0
		if pntr is None:
			return QModelIndex()
		elif pntr in rows:
			parent_id = None
		else:
			if pntr in rows_t:
				parent_id = rows[rows_t.index(pntr)]
				parent_row = rows_t.index(pntr)

		parent_col = 0
		return self.createIndex(parent_row, parent_col, parent_id)

	def index(self, row, col, parent: QModelIndex = None, *args, **kwargs):
		if parent.internalPointer() is None:
			return self.createIndex(row, col, rows[row])
		if parent.internalPointer() in rows:
			parent_row = parent.row()
			return self.createIndex(row, col, rows_t[parent_row])

		return QModelIndex()

	def set_material(self, material):
		if self._material is not None:
			self._material.remove_change_handler(self.on_material_changed)
		self._material = material
		if material is not None:
			material.add_change_handler(self.on_material_changed)
		self.layoutChanged.emit()

	def on_material_changed(self, event):
		self.layoutChanged.emit()

	def headerData(self, p_int, orientation, int_role=None):
		if int_role == Qt.DisplayRole:
			if orientation == Qt.Vertical:
				return p_int
			else:
				return col_header[p_int]

		else:
			return

	def flags(self, model_index: QModelIndex):
		col = model_index.column()
		row = model_index.row()
		pntr = model_index.internalPointer()
		if (pntr == "Name" or pntr == "Number") and col == 1:
			default_flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
		elif pntr in rows_t:
			default_flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
		else:
			default_flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
		return default_flags
