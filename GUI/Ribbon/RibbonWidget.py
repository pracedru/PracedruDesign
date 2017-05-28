from PyQt5.QtWidgets import *
from GUI.Ribbon.RibbonTab import RibbonTab
from GUI import gui_scale, tr

__author__ = 'magnus'


class RibbonWidget(QTabWidget):
    def __init__(self, main_window):
        QWidget.__init__(self, main_window)

        self.setMaximumHeight(150*gui_scale())
        self.setMinimumHeight(100*gui_scale())

    def add_ribbon_tab(self, name):
        ribbon_tab = RibbonTab(self, tr(name, "ribbon"))
        self.addTab(ribbon_tab, name)
        return ribbon_tab