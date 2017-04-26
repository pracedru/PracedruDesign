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
from GUI.Widgets.DrawingView import DrawingViewWidget
from GUI.Widgets.PartView import PartViewWidget
from GUI.Widgets.SketchView import SketchViewWidget

__author__ = 'mamj'


class ViewWidget(QStackedWidget):
    def __init__(self, main_window, document):
        QStackedWidget.__init__(self, main_window)
        self._doc = document
        self._sketchView = SketchViewWidget(self, document, main_window)
        self._partView = PartViewWidget(self, document)
        self._drawingView = DrawingViewWidget(self, document, main_window)
        self.addWidget(self._sketchView)
        self.addWidget(self._partView)
        self.addWidget(self._drawingView)

    @property
    def sketch_view(self):
        return self._sketchView

    @property
    def drawing_view(self):
        return self._drawingView

    def set_sketch_view(self, sketch):
        self.setCurrentIndex(0)
        self._sketchView.set_sketch(sketch)

    def set_drawing_view(self, drawing):
        self.setCurrentIndex(2)
        self._drawingView.set_drawing(drawing)

    def on_add_line(self):
        if self.currentIndex() == 0:
            self._sketchView.on_add_line()

    def on_find_all_similar(self):
        if self.currentIndex() == 0:
            self._sketchView.on_find_all_similar()

    def on_insert_text(self):
        if self.currentIndex() == 0:
            self._sketchView.on_insert_text()

    def on_kp_selection_changed_in_table(self, selected_key_points):
        self._sketchView.set_selected_key_points(selected_key_points)

    def on_edge_selection_changed_in_table(self, selected_edges):
        self._sketchView.set_selected_edges(selected_edges)

    def on_zoom_fit(self):
        if self.currentIndex() == 0:
            self._sketchView.on_zoom_fit()
        elif self.currentIndex() == 2:
            self._drawingView.on_zoom_fit()

    def on_add_fillet(self):
        if self.currentIndex() == 0:
            self._sketchView.on_add_fillet()

    def on_add_circle(self):
        if self.currentIndex() == 0:
            self._sketchView.on_add_circle()

    def on_set_similar_x_coordinates(self):
        if self.currentIndex() == 0:
            self._sketchView.on_set_similar_x_coordinates()

    def on_insert_attribute(self):
        if self.currentIndex() == 0:
            self._sketchView.on_insert_attribute()