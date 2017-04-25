from PyQt5.QtCore import QMargins, QItemSelection, QEvent, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListView, QTableView, QDockWidget

from Data import Document
from GUI import gui_scale

from GUI.Models.AreasModel import AreasModel
from GUI.Widgets.AreaTableView import AreaTableView
from GUI.Widgets.EdgesTableView import EdgesTableView
from GUI.Widgets.KeyPointsTableView import KeyPointsTableView

__author__ = 'mamj'


class GeometryDock(QDockWidget):
    def __init__(self, main_window, doc: Document):
        QDockWidget.__init__(self, main_window)
        self._main_window = main_window
        self._doc = doc
        self._widget = QWidget(self)
        self.setWidget(self._widget)
        guiscale = gui_scale()
        self.setWindowTitle("Geometry")
        self.setObjectName("geometryDock")
        self.setMinimumWidth(200*guiscale)
        layout = QVBoxLayout()
        self._widget.setLayout(layout)
        # self.areas_table_widget = AreaTableView(self, doc, main_window)
        # layout.addWidget(self.areas_table_widget)
        layout.setContentsMargins(QMargins(0, 0, 0, 0))

        self.edges_table_widget = EdgesTableView(self, doc, main_window)
        layout.addWidget(self.edges_table_widget)

        self.kps_table_widget = KeyPointsTableView(self, doc, main_window)
        layout.addWidget(self.kps_table_widget)

    def set_sketch(self, sketch):
        self.edges_table_widget.set_sketch(sketch)
        self.kps_table_widget.set_sketch(sketch)

    def set_list(self, list):
        pass

    def on_edge_selection_changed(self, selected_edges):
        self.edges_table_widget.set_selected_edges(selected_edges)
        kps = []
        for edge in selected_edges:
            for kp in edge.get_end_key_points():
                kps.append(kp)
        if len(kps) > 0:
            self.kps_table_widget.set_selected_kps(kps)

    def on_kp_selection_changed(self, selected_key_points):
        self.kps_table_widget.set_selected_kps(selected_key_points)

    def on_area_selection_changed(self, selected_areas):
        self.areas_table_widget.set_selected_areas(selected_areas)
