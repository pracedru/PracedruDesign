import random
from PyQt5 import QtGui
from PyQt5.QtCore import QPointF, QRectF, QPoint, QLocale, Qt, QEvent
from PyQt5.QtGui import QLinearGradient, QColor, QPen, QPolygon, QPainterPath, QPolygonF, QBrush, QPainter
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QStackedWidget
from PyQt5.QtWidgets import QWidget, QInputDialog, QDialog, QMessageBox
from math import cos, pi, sin, sqrt, ceil, asin, tan

import Business
from Data.Areas import Area
from Data.Components import Component
from Data.Sketch import Edge
from Data.Geometry import Geometry
from Data.Mesh import MeshDefinition
from Data.Sweeps import SweepDefinition
from Data.Vertex import Vertex
from GUI import is_dark_theme
from GUI.Widgets.PartView import PartViewWidget
from GUI.Widgets.SketchView import SketchViewWidget

__author__ = 'mamj'


class ViewWidget(QStackedWidget):
    def __init__(self, main_window, document):
        QStackedWidget.__init__(self, main_window)
        self._doc = document
        self._sketchView = SketchViewWidget(self, document, main_window)
        self._partView = PartViewWidget(self, document)
        self.addWidget(self._sketchView)
        self.addWidget(self._partView)

    def set_sketch_view(self, sketch):
        self.setCurrentIndex(0)
        self._sketchView.set_sketch(sketch)

    def on_add_line(self):
        if self.currentIndex() == 0:
            self._sketchView.on_add_line()

    def on_find_all_similar(self):
        if self.currentIndex() == 0:
            self._sketchView.on_find_all_similar()

    def on_kp_selection_changed_in_table(self, selected_key_points):
        self._sketchView.set_selected_key_points(selected_key_points)

    def on_edge_selection_changed_in_table(self, selected_edges):
        self._sketchView.set_selected_edges(selected_edges)