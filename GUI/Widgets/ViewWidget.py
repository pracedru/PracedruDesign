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
from GUI.Widgets.SketchView import SketchViewWidget

__author__ = 'mamj'


class ViewWidget(QStackedWidget):
    def __init__(self, parent, document):
        QStackedWidget.__init__(self, parent)
        self._doc = document
        self.addWidget(SketchViewWidget(self, document))
