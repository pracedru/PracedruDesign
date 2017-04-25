from PyQt5.QtWidgets import QDockWidget
from PyQt5.QtWidgets import QTableView

from Data.Document import Document
from GUI import gui_scale
from GUI.Models.PropertiesModel import PropertiesModel


class PropertiesDock(QDockWidget):
    def __init__(self, main_window, doc: Document):
        QDockWidget.__init__(self, main_window)
        self.setWindowTitle("Properties")
        self.setObjectName("PropertiesDock")
        self._doc = doc
        self._table_view = QTableView(self)
        self.setWidget(self._table_view)
        self._model = PropertiesModel(doc)
        guiscale = gui_scale()
        self._table_view.setModel(self._model)
        self._table_view.setColumnWidth(0, 250 * guiscale)

    def set_item(self, item):
        self._model.set_item(item)