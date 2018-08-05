from PyQt5.QtWidgets import QTableView
from GUI.init import gui_scale
from GUI.Models.CalcTableModel import CalcTableModel


class CalcTableView(QTableView):
	def __init__(self, parent, doc, main_window):
		QTableView.__init__(self, parent)
		self._doc = doc
		self._main_window = main_window
		self._guiscale = gui_scale()
		self._calc_table_model = CalcTableModel(self._doc)
		self.setModel(self._calc_table_model)
		self.selectionModel().selectionChanged.connect(self.on_calc_table_selection_changed)

	def on_calc_table_selection_changed(self):
		pass

	def set_calc_table(self, calc_table):
		self._calc_table_model.set_table(calc_table)
