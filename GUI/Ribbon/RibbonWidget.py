from PyQt5.QtWidgets import *
from GUI.Ribbon.RibbonTab import RibbonTab
from GUI.init import gui_scale, tr

__author__ = 'magnus'


class RibbonWidget(QTabWidget):
	def __init__(self, main_window):
		QWidget.__init__(self, main_window)

		self.setMaximumHeight(150 * gui_scale())
		self.setMinimumHeight(100 * gui_scale())
		self._tabs = {}

	def add_ribbon_tab(self, name):
		ribbon_tab = RibbonTab(self, tr(name, "ribbon"))
		self.addTab(ribbon_tab, name)
		self._tabs[name] = ribbon_tab
		return ribbon_tab

	def get_ribbon_tab(self, name):
		if name in self._tabs:
			return self._tabs[name]
		return self.add_ribbon_tab(name)
