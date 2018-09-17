from PyQt5.QtCore import QEvent
from PyQt5.QtCore import QItemSelectionModel
from PyQt5.QtCore import QMargins
from PyQt5.QtCore import QSortFilterProxyModel
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QTableView, QVBoxLayout, QHBoxLayout, QPushButton, QInputDialog, QMessageBox, QLabel, QComboBox

import Business
from Business.ParameterActions import add_parameter
from GUI.Widgets.SimpleDialogs import StandardTypeDialog
from GUI.init import gui_scale
from GUI.Models.ParametersModel import ParametersModel


class ParametersWidget(QWidget):
	def __init__(self, main_window, document):
		QWidget.__init__(self, main_window)
		# self._document = document
		self._main_window = main_window
		guiscale = gui_scale()
		self._ignore_type_standard_change = False
		self._gui_scale = guiscale
		self._parameters = document.get_parameters()
		self.parameters_table = QTableView(self)
		self.parameters_model = ParametersModel(self._parameters)
		self.parameters_model.add_user_input_handler(self.on_user_input)
		self.parameters_sort_model = QSortFilterProxyModel()
		self.parameters_sort_model.setSourceModel(self.parameters_model)
		self.parameters_table.setModel(self.parameters_sort_model)
		self.parameters_table.setSortingEnabled(True)
		self.parameters_sort_model.setSortCaseSensitivity(False)
		layout = QVBoxLayout()
		self.setLayout(layout)
		predefined_standards_widget = QWidget(self)
		predefined_standards_widget.setLayout(QHBoxLayout())
		predefined_standards_widget.layout().addWidget(QLabel("Standard"))
		self._standards_combobox = QComboBox(predefined_standards_widget)
		self._standards_combobox.setMinimumWidth(110*guiscale)
		predefined_standards_widget.layout().addWidget(self._standards_combobox)
		predefined_standards_widget.layout().addWidget(QLabel("Type"))
		self._type_combobox = QComboBox(predefined_standards_widget)
		predefined_standards_widget.layout().addWidget(self._type_combobox)
		self._type_combobox.setMinimumWidth(110*guiscale)
		self._standards_combobox.currentTextChanged.connect(self.on_standard_changed)
		self._type_combobox.currentTextChanged.connect(self.on_type_changed)
		add_type_button = QPushButton("Manage")
		add_type_button.clicked.connect(self.on_manage)
		predefined_standards_widget.layout().layout().addWidget(add_type_button)

		layout.addWidget(predefined_standards_widget)
		layout.addWidget(self.parameters_table)
		layout.setContentsMargins(QMargins(0, 0, 0, 0))
		self.parameters_table.setColumnWidth(0, 120 * guiscale)
		self.parameters_table.setColumnWidth(1, 150 * guiscale)
		self.parameters_table.setColumnWidth(2, 80 * guiscale)
		self.parameters_table.setColumnWidth(3, 40 * guiscale)
		buttons_widget = QWidget()
		buttons_widget.setLayout(QHBoxLayout())
		add_button = QPushButton("Add Parameter")
		add_button.clicked.connect(self.on_add_parameter)
		buttons_widget.layout().addWidget(add_button)
		delete_button = QPushButton("Delete Parameter")
		buttons_widget.layout().addWidget(delete_button)
		delete_button.clicked.connect(self.on_delete)
		governor_button = QPushButton("Set governor")
		governor_button.clicked.connect(self.on_set_governor)
		buttons_widget.layout().addWidget(governor_button)
		layout.addWidget(buttons_widget)
		self.installEventFilter(self)
		# self.update_hide_parameters()
		self.parameters_table.selectionModel().selectionChanged.connect(self.on_param_selection_changed)

	def set_parameters(self, params):
		if params == self._parameters:
			return
		self._ignore_type_standard_change = True
		if self._parameters is not None:
			self._parameters.remove_change_handler(self.on_parameters_changed)
		self._parameters = params
		self._parameters.add_change_handler(self.on_parameters_changed)
		self.parameters_model.set_parameters(params)
		self.parameters_table.resizeColumnsToContents()
		self.update_standards(params)
		self.update_types(params)
		self.update_hide_parameters()
		self._ignore_type_standard_change = False

	def update_standards(self, params):
		self._standards_combobox.clear()
		options = list(params.standards)
		self._standards_combobox.addItems(options)
		if params.standard in options:
			self._standards_combobox.setCurrentIndex(options.index(params.standard))


	def update_types(self, params):
		self._type_combobox.clear()
		options = list(params.get_types_from_standard(params.standard))
		self._type_combobox.addItems(options)
		if params.type != "" and params.type in options:
			self._type_combobox.setCurrentIndex(options.index(params.type))

	def on_parameters_changed(self, event):
		if event.type == event.ObjectAdded or event.type == event.ObjectRemoved:
			self.update_hide_parameters()

	def on_manage(self):
		std = StandardTypeDialog(self, self._parameters)
		std.exec_()
		self.update_standards(self._parameters)
		self.update_types(self._parameters)
		# self._ignore_type_standard_change = True
		# self._parameters.make_type(self._parameters.standard, "New Type")
		# self._type_combobox.clear()
		# options = list(self._parameters.types)
		# self._type_combobox.addItems(options)
		# self._type_combobox.setCurrentIndex(options.index(self._parameters.type))
		# self._ignore_type_standard_change = False

	def on_type_changed(self, value):
		if not self._ignore_type_standard_change:
			self._parameters.type = value
			self.on_user_input(None)

	def on_standard_changed(self, value):
		if not self._ignore_type_standard_change:
			self._parameters.standard = value
			self.update_types(self._parameters)

	def on_add_parameter(self):
		# self.parent().parent().on_add_parameter()
		add_parameter(self._parameters)
		self.update_hide_parameters()
		ndx = self.parameters_model.index(self.parameters_model.rowCount() - 1, 0)
		index = self.parameters_sort_model.mapFromSource(ndx)
		self.parameters_table.scrollTo(index)
		sm = self.parameters_table.selectionModel()
		sm.setCurrentIndex(index, QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)

	def on_set_governor(self):
		rows = self.parameters_table.selectionModel().selectedRows()
		params = []
		for param in self._parameters.get_all_parameters():
			params.append(param.name)
		params.sort()
		value = QInputDialog.getItem(self, "Set parameter", "Parameter:", params, 0, False)
		governor_parameter = self._parameters.get_parameter_by_name(value[0])
		for ndx in rows:
			index = self.parameters_sort_model.mapToSource(ndx)
			row = index.row()
			param = self._parameters.get_parameter_item(row)
			if param is not governor_parameter:
				param.value = (governor_parameter.name + "+" + str(round(param.value - governor_parameter.value, 4))).replace("+-", '-')

	def on_delete(self):
		txt = "Are you sure you want to delete this parameter?"
		ret = QMessageBox.warning(self, "Delete parameter?", txt, QMessageBox.Yes | QMessageBox.Cancel)
		if ret == QMessageBox.Yes:
			selection_model = self.parameters_table.selectionModel()
			indexes = selection_model.selectedIndexes()
			selected_rows = set()
			for index in indexes:
				index = self.parameters_sort_model.mapToSource(index)
				selected_rows.add(index.row())
			self.parameters_model.remove_rows(selected_rows)

	def eventFilter(self, obj, event):
		if event.type() == QEvent.KeyPress:
			if event.key() == Qt.Key_Delete:
				self.on_delete()
				return True
		return False

	def update_hide_parameters(self):
		rowcount = self.parameters_sort_model.rowCount()
		for i in range(rowcount):
			index = self.parameters_model.index(i, 0)
			index = self.parameters_sort_model.mapFromSource(index)
			row = index.row()
			if not self._main_window.states.show_params:
				hide = self.parameters_model.row_hidden(i)
				if hide:
					self.parameters_table.hideRow(row)
				else:
					self.parameters_table.showRow(row)
			else:
				self.parameters_table.showRow(i)

	def on_param_selection_changed(self, selection):
		selection_model = self.parameters_table.selectionModel()
		indexes = selection_model.selectedIndexes()
		selected_parameters = set()
		for index in indexes:
			ndx = self.parameters_sort_model.mapToSource(index)
			selected_parameters.add(self.parameters_model.get_parameter_from_row(ndx.row()))
		self._main_window.on_param_selection_changed_in_parameters_widget(list(selected_parameters))

	def on_user_input(self, event):
		self._main_window.on_update_view()