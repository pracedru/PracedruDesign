from PyQt5.QtCore import *
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMessageBox

from Business.ParameterActions import set_parameter, set_parameter_name, delete_parameters
from Data.Parameters import *
from GUI.init import formula_from_locale, formula_to_locale, gui_scale

__author__ = 'mamj'

col_header = ["Name", "Expression", "Value", 'Hide']


class ParametersModel(QAbstractTableModel):
	def __init__(self, parameters: Parameters):
		QAbstractItemModel.__init__(self)
		self._parameters = parameters
		parameters.add_change_handler(self.on_parameters_changed)
		self.old_row_count = 0
		self._gui_scale = gui_scale()
		self._columns_widths = [120, 150, 80, 40]
		self._instance = None
		self._user_input_handlers = []

	@property
	def instance(self):
	    return self._instance

	@instance.setter
	def instance(self, value):
		self._instance = value

	def add_user_input_handler(self, user_input_handler):
		self._user_input_handlers.append(user_input_handler)

	def on_user_input(self):
		for input_handler in self._user_input_handlers:
			input_handler(None)

	def set_parameters(self, params):

		self._parameters.remove_change_handler(self.on_parameters_changed)
		self._parameters = params
		if issubclass(type(params), ParametersInstance):
			self._instance = params.uid
		else:
			self._instance = None
		self._parameters.add_change_handler(self.on_parameters_changed)
		self.modelReset.emit()

	def rowCount(self, model_index=None, *args, **kwargs):
		return self._parameters.length_all

	def columnCount(self, model_index=None, *args, **kwargs):
		return 4

	def data(self, model_index: QModelIndex, int_role=None):
		col = model_index.column()
		row = model_index.row()
		data = None
		if int_role == Qt.DisplayRole:
			param_item = self._parameters.get_parameter_item(row)
			if col == 0:
				data = param_item.full_name
			elif col == 1:
				if param_item is Parameters:
					param = param_item.get_parameter(col - 2)
				else:
					param = param_item
				data = formula_to_locale(param.get_instance_formula(self._instance))
			elif col == 2:
				if param_item is Parameters:
					param = param_item.get_parameter(col - 2)
				else:
					param = param_item
				data = param.get_instance_value(self._instance)
			elif col == 3:
				data = None  # param_item.hidden
		elif int_role == Qt.TextAlignmentRole:
			if col == 0:
				return None
			else:
				param_item = self._parameters.get_parameter_item(row)
				if param_item is not None:
					if col == 1:
						if type(param_item.formula) is str:
							return Qt.AlignLeft | Qt.AlignVCenter
						else:
							return Qt.AlignRight | Qt.AlignVCenter
					else:
						if type(param_item.value) is str:
							return Qt.AlignLeft | Qt.AlignVCenter
						else:
							return Qt.AlignRight | Qt.AlignVCenter
		elif int_role == Qt.CheckStateRole:
			param_item = self._parameters.get_parameter_item(row)
			if col == 3:
				if param_item.hidden:
					return Qt.Checked
				else:
					return Qt.Unchecked
		elif int_role == Qt.EditRole:
			param_item = self._parameters.get_parameter_item(row)
			if col == 0:
				data = param_item.name
			elif col == 1:
				if param_item is Parameters:
					param = param_item.get_parameter(col - 1)
				else:
					param = param_item
				if param.get_instance_formula(self._instance) != "":
					data = data = formula_to_locale(param.get_instance_formula(self._instance))
				else:
					data = QLocale().toString(param.get_instance_value(self._instance))
			elif col == 2:
				if param_item is Parameters:
					param = param_item.get_parameter(col - 2)
				else:
					param = param_item
				if param.formula != "":
					data = formula_to_locale(param.get_instance_formula(self._instance))
				else:
					data = QLocale().toString(param.get_instance_value(self._instance))
		elif int_role == Qt.BackgroundColorRole:
			param_item = self._parameters.get_parameter_item(row)
			if self._parameters.param_in_current_type(param_item):
				return QColor(80,120,200,50)
			else:
				return None
		return data

	def setData(self, model_index: QModelIndex, value: QVariant, int_role=None):
		col = model_index.column()
		row = model_index.row()
		param_item = self._parameters.get_parameter_item(row)
		if col == 0:
			set_parameter_name(param_item, value)
			# param_item.name = value
			self.on_user_input()
			return True
		elif col == 1 or col == 2:
			if param_item is Parameters:
				param = param_item.get_parameter(col - 1)
			else:
				param = param_item
			if isinstance(value, float):
				set_parameter(param, value, self._instance)
				# param.value = value
				self.on_user_input()
				return True
			parsed = QLocale().toDouble(value)
			if parsed[1]:
				# param.value = parsed[0]
				try:
					set_parameter(param, parsed[0], self._instance)
				except Exception as e:
					self._parameters.document.set_status(str(e))
			else:
				try:
					if value == "":
						set_parameter(param, 0.0, self._instance)
					# param.value = 0.0
					else:
						set_parameter(param, formula_from_locale(value), self._instance)
				# param.value = formula_from_locale(value)
				except Exception as ex:
					self._parameters.document.set_status(str(ex))
			self.on_user_input()
			return True
		elif col == 3:
			if int_role == Qt.CheckStateRole:
				hide = value == Qt.Checked
				param_item.hidden = hide
		return False

	def on_parameters_changed(self, event):
		if issubclass(type(event.sender), ParametersBase):
			if event.type == ChangeEvent.ObjectChanged and event.object == event.sender:
				self.modelAboutToBeReset.emit()
				self.modelReset.emit()
		if type(event.sender) is Parameter or type(event.object) is Parameter:
			if event.type == event.BeforeObjectAdded:
				parent = QModelIndex()
				row = self.rowCount()
				self.beginInsertRows(parent, row, row)
			if event.type == event.ObjectAdded:
				self.endInsertRows()
			if event.type == event.BeforeObjectRemoved:
				row = self._parameters.get_index_of(event.object)
				self.beginRemoveRows(QModelIndex(), row, row)
			if event.type == event.ObjectRemoved:
				self.endRemoveRows()
			if event.type == event.ValueChanged:
				param = event.sender
				row = self._parameters.get_index_of(param)
				left = self.createIndex(row, 0)
				right = self.createIndex(row, 3)
				self.dataChanged.emit(left, right)
			if event.type == event.HiddenChanged:
				print("hidden changed")
				param = event.sender
				if type(param) is Parameter:
					row = self._parameters.get_index_of(param)
					left = self.createIndex(row, 3)
					right = self.createIndex(row, 3)
					self.dataChanged.emit(left, right)

	def flags(self, model_index: QModelIndex):
		default_flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
		if model_index.column() == 3:
			default_flags = Qt.ItemIsUserCheckable | Qt.ItemIsEnabled
		return default_flags

	def headerData(self, p_int, orientation, int_role=None):
		if int_role == Qt.DisplayRole:
			if orientation == Qt.Vertical:
				return p_int
			else:
				return col_header[p_int]
		elif int_role == Qt.SizeHintRole:
			if orientation == Qt.Horizontal:
				return QSize(self._columns_widths[p_int] * self._gui_scale, 22 * self._gui_scale);
		else:
			return None

	def get_parameters_object(self):
		return self._parameters

	def remove_rows(self, rows):
		params = []
		for row in rows:
			params.append(self._parameters.get_parameter_item(row))

		delete_parameters(self._parameters, params)

	def row_hidden(self, row):
		return self._parameters.get_parameter_item(row).hidden

	def get_parameter_from_row(self, row):
		return self._parameters.get_parameter_item(row)

	def get_row_from_parameter(self, parameter):
		return self._parameters.get_index_of(parameter)
